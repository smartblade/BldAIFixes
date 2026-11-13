"""Compile BldMystery with Visual C++ 6.0 and compare it with the binaries.

Commands:

    build   BLDMYSTERY WORK [--module M] [--file F]  copy, patch and compile
    compare BLDMYSTERY WORK [--module M] [--json F]  compare implemented
                                                     procedures
    diff    BLDMYSTERY WORK PROCEDURE...             instruction differences
    stack   BLDMYSTERY WORK PROCEDURE                local variables with
                                                     their offsets in the
                                                     binary

BLDMYSTERY is a checkout of BldMystery, WORK is a working directory for the
patched copy of the sources (WORK/src) and compiled objects
(WORK/obj/MODULE). Procedures are mangled names, e.g.
'?Build@B_OctTree@@QAEXABVB_Map@@N@Z'.

The compiler is run as the command in the VC6_CL environment variable,
'cl' by default: in a Windows command prompt or Git Bash after VCVARS32.BAT
of Visual C++ 6.0. On Linux and macOS it is run by Wine, e.g.
VC6_CL="wine CL.EXE" with WINEPATH set to the VC98/Bin and Common/MSDev98/Bin
directories, and INCLUDE set to VC98/Include (Z:/... paths of Wine). Paths
passed to a compiler run by Wine are converted to Z: paths.

Instructions are disassembled with the capstone package
('pip install capstone') or with ndisasm of NASM when it is installed.
"""
import argparse
import concurrent.futures
import difflib
import json
import os
import re
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare_obj  # noqa: E402
from stack_layout import bucket  # noqa: E402

# Module: (directory of asm files, source directories, extra options).
# A source directory is a name or (name, extra options, files): BBLibc.dll
# contains only some files of AnalyticGeometry, compiled with the sources
# of BBLibc (calls of B_IDataFile are direct, not through imports).
MODULES = {
    "Blade": (
        "Blade",
        [
            "Blade", "App", "BWorld", "Control", "View", "enemies",
            "Entities", "Math", "NetMod", "Person", "Sound",
            "AnalyticGeometry", "Physics",
        ],
        [],
    ),
    "BBLibc": (
        "BBLibc",
        [
            "BBLibc",
            (
                "AnalyticGeometry", ["/DBBLIBC_LIB_EXPORT"],
                ["BoundingBox.cpp", "Matrix.cpp", "Plane.cpp", "Vector.cpp"],
            ),
        ],
        ["/DBUILD_LIB"],
    ),
    "rOpenGL": ("Raster/rOpenGL3", ["Raster/rOpenGL3", "AnalyticGeometry"],
                []),
}

OPTIONS = [
    "/nologo", "/c", "/MD", "/Od", "/Ob1", "/Oi", "/Zp4", "/GR-",
    "/DBLD_NATIVE", "/Doverride=", "/FAs",
]

# Include directories relative to the source tree
INCLUDE_DIRS = [
    "Python-1.5.2/Include", "Python-1.5.2/PC", ".", "include", "Blade",
]


# Patches of sources for Visual C++ 6.0: (file, old text, new text, reason)
PATCHES = [
    (
        "include/bld_system.h",
        "#include <bld_assert.h>",
        "#include <assert.h>",
        "the original binaries use assert of Visual C++ 6.0",
    ),
    # array.h is in include in older sources and in BBLibc in newer ones
    *[
        patch
        for array_h in ("include/array.h", "BBLibc/array.h")
        for patch in (
            (
                array_h,
                # The second loop of a block declaring 'i' in the first one
                lambda text: _replace_after(
                    text, "for (unsigned int i = 0; i < index; i++)",
                    "for (unsigned int i = index + 1;", "for (i = index + 1;"),
                None,
                "a variable of 'for' is in the enclosing block in "
                "Visual C++ 6.0",
            ),
            (
                array_h,
                # B_PtrArray is named B_Array in newer sources
                lambda text: _replace_first(
                    text,
                    [
                        ("    B_PtrArray(increment)\n",
                         "    B_PtrArray<TYPE>(increment)\n"),
                        ("    B_Array(increment)\n",
                         "    B_Array<TYPE>(increment)\n"),
                    ]),
                None,
                "Visual C++ 6.0 needs arguments of templates of base classes",
            ),
        )
    ],
    (
        "App/App.cpp",
        # Only after the loop over gbl_ag_textures declaring 'i'
        lambda text: _replace_after(
            text,
            "for (unsigned int i = 0; i < gbl_ag_textures.size; i++)",
            "        for (unsigned int i = 0; i < this->afterFrameFuncs.size;",
            "        for (i = 0; i < this->afterFrameFuncs.size;"),
        None,
        "a variable of 'for' is in the enclosing block in Visual C++ 6.0",
    ),
    (
        "Blade/WinClock.cpp",
        "#include <intrin.h>",
        "unsigned int __readeflags(); void __writeeflags(unsigned int); "
        "void __cpuid(int *, int); unsigned __int64 __rdtsc();",
        "Visual C++ 6.0 has no intrin.h",
    ),
]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__[__doc__.index("\n"):])
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("bldmystery")
    build_parser.add_argument("work")
    build_parser.add_argument("--module", choices=MODULES)
    build_parser.add_argument(
        "--file", action="append",
        help="compile only this file (relative to src), may be repeated")
    build_parser.add_argument("--jobs", type=int, default=os.cpu_count())
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("bldmystery")
    compare_parser.add_argument("work")
    compare_parser.add_argument("--module", choices=MODULES)
    compare_parser.add_argument("--json", help="write results to the file")
    diff_parser = subparsers.add_parser("diff")
    diff_parser.add_argument("bldmystery")
    diff_parser.add_argument("work")
    diff_parser.add_argument("procedure", nargs="+")
    diff_parser.add_argument("--module", choices=MODULES)
    diff_parser.add_argument("--max-lines", type=int, default=60)
    stack_parser = subparsers.add_parser("stack")
    stack_parser.add_argument("bldmystery")
    stack_parser.add_argument("work")
    stack_parser.add_argument("procedure")
    stack_parser.add_argument("--module", choices=MODULES)
    args = parser.parse_args()
    modules = [args.module] if getattr(args, "module", None) else list(
        MODULES)
    if args.command == "build":
        return build(args.bldmystery, args.work, modules, args.file, args.jobs)
    if args.command == "compare":
        return compare(args.bldmystery, args.work, modules, args.json)
    if args.command == "diff":
        return diff(args.bldmystery, args.work, modules, args.procedure,
                    args.max_lines)
    return stack(args.bldmystery, args.work, modules, args.procedure)


# Building

def build(bldmystery, work, modules, files, jobs):
    src = os.path.join(work, "src")
    copy_sources(os.path.join(bldmystery, "src"), src)
    compiler = Compiler(src)
    tasks = []
    for module in modules:
        out_dir = os.path.join(work, "obj", module)
        os.makedirs(out_dir, exist_ok=True)
        for source, options in module_sources(src, module):
            if files and not any(_same_path(source, f) for f in files):
                continue
            tasks.append((module, source, out_dir, options))
    print("Compiling {} files...".format(len(tasks)))
    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        results = pool.map(
            lambda task: (task, compiler.compile(*task[1:])), tasks)
        for (module, source, out_dir, options), errors in results:
            if errors:
                failed.append(source)
                print("{}: {}".format(source, errors[0]))
    print("Compiled {} files, {} failed".format(
        len(tasks) - len(failed), len(failed)))
    return 1 if failed else 0


def copy_sources(src, dst):
    """Copy sources and apply patches for Visual C++ 6.0."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "*.asm", "*.inc", "raw.txt", "reloc.txt", "*.str"))
    for file_name, old, new, reason in PATCHES:
        path = os.path.join(dst, file_name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="cp1251", newline="") as f:
            text = f.read()
        crlf = "\r\n" in text
        text = text.replace("\r\n", "\n")
        if callable(old):
            new_text = old(text)
        elif old in text:
            new_text = text.replace(old, new)
        else:
            new_text = None
        if new_text is None:
            print("Patch of {} is not applied ({})".format(file_name, reason))
            continue
        text = new_text
        if crlf:
            text = text.replace("\n", "\r\n")
        with open(path, "w", encoding="cp1251", newline="") as f:
            f.write(text)


def _replace_first(text, replacements):
    """Apply the first of (old, new) found in the text, None if none."""
    for old, new in replacements:
        if old in text:
            return text.replace(old, new)
    return None


def _replace_after(text, anchor, old, new):
    """Replace the first 'old' after 'anchor', None if not found."""
    start = text.find(anchor)
    if start < 0:
        return None
    index = text.find(old, start)
    if index < 0:
        return None
    return text[:index] + new + text[index + len(old):]


def module_sources(src, module):
    """(source file relative to src, compiler options) of the module."""
    sources = []
    for entry in MODULES[module][1]:
        if isinstance(entry, str):
            directory, extra_options, only_files = entry, [], None
        else:
            directory, extra_options, only_files = entry
        options = MODULES[module][2] + extra_options
        path = os.path.join(src, directory)
        if not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d != "asm"]
            # Sources of subdirectories, e.g. App/Windows, one level deep
            if os.path.relpath(root, path).count(os.sep) > 0:
                continue
            for file_name in sorted(files):
                if not file_name.lower().endswith(".cpp"):
                    continue
                if only_files is not None and file_name not in only_files:
                    continue
                sources.append((os.path.relpath(
                    os.path.join(root, file_name), src).replace(
                        os.sep, "/"), options))
    return sources


def _same_path(first, second):
    return first.replace("\\", "/").lower() == second.replace(
        "\\", "/").lower()


def object_name(source):
    return os.path.splitext(source)[0].replace("/", "_")


def split_command(command):
    """Split a command line, keeping backslashes of Windows paths."""
    if os.name != "nt":
        return shlex.split(command)
    return [
        part[1:-1] if len(part) > 1 and part[0] == part[-1] == '"' else part
        for part in shlex.split(command, posix=False)
    ]


class Compiler:
    def __init__(self, src):
        self._command = split_command(os.environ.get("VC6_CL", "cl"))
        self._wine = os.path.basename(self._command[0]).lower() in (
            "wine", "wine64")
        self._src = os.path.abspath(src)
        include = [self._path(os.path.join(self._src, d))
                   for d in INCLUDE_DIRS]
        self._env = dict(os.environ)
        if os.environ.get("INCLUDE"):
            include.append(os.environ["INCLUDE"])
        self._env["INCLUDE"] = ";".join(include)
        if self._wine:
            self._env.setdefault("WINEDEBUG", "-all")

    def _path(self, path):
        """Path for the compiler: Z: path of Wine or the native path."""
        path = os.path.abspath(path)
        if self._wine:
            return "Z:" + path.replace("\\", "/")
        return path

    def compile(self, source, out_dir, options):
        """Compile the source, return error lines."""
        name = object_name(source)
        args = self._command + OPTIONS + options + [
            "/Fa{}.asm".format(name), "/Fo{}.obj".format(name),
            self._path(os.path.join(self._src, source)),
        ]
        result = subprocess.run(
            args, cwd=out_dir, env=self._env, capture_output=True,
            text=True, errors="replace")
        output = (result.stdout + result.stderr).replace("\r", "")
        with open(os.path.join(out_dir, name + ".log"), "w") as f:
            f.write(output)
        errors = [line for line in output.split("\n") if " error " in line]
        obj_file = os.path.join(out_dir, name + ".obj")
        if not errors and (result.returncode != 0 or
                           not os.path.exists(obj_file)):
            errors = [line for line in output.split("\n") if line] or [
                "compiler failed with code {}".format(result.returncode)]
        return errors


# Comparison

class ModuleData:
    """Implemented procedures, the binary and compiled objects of a module."""

    def __init__(self, bldmystery, work, module):
        self.module = module
        asm_dir = os.path.join(bldmystery, "src", MODULES[module][0], "asm")
        self.memory, _ = compare_obj.read_raw(
            os.path.join(asm_dir, "raw.txt"))
        self.procedures = _read_procedures(asm_dir)
        self.implemented = _read_implemented(asm_dir)
        self._obj_dir = os.path.join(work, "obj", module)
        self._objects = None
        self._image_range = None

    def objects(self):
        if self._objects is None:
            self._objects = []
            if os.path.isdir(self._obj_dir):
                for file_name in sorted(os.listdir(self._obj_dir)):
                    if file_name.endswith(".obj"):
                        path = os.path.join(self._obj_dir, file_name)
                        self._objects.append(
                            (path, compare_obj.ObjFile(path)))
        return self._objects

    def compiled(self, name):
        """(object path, code, mask, relocations, mask of relocations only)
        of the procedure, the mask hides relocations and line numbers of
        assert."""
        for path, obj in self.objects():
            for symbol in obj.functions():
                if symbol.name == name:
                    code, relocations_mask, relocations = \
                        obj.get_function_code(symbol)
                    mask = list(relocations_mask)
                    for offset, size in assert_lines(code, relocations):
                        for i in range(offset, offset + size):
                            mask[i] = True
                    return path, code, mask, relocations, relocations_mask
        return None

    def image_range(self):
        """Range of addresses of the image: raw.txt holds the code only,
        data of the image follows it (16 MB from the image base)."""
        if self._image_range is None:
            base = min(self.memory) & ~0xFFFF
            self._image_range = (base, base + 0x1000000)
        return self._image_range

    def original(self, address, size):
        return bytes(self.memory.get(address + i, 0) for i in range(size))


def _read_procedures(asm_dir):
    procedures = {}
    with open(os.path.join(asm_dir, "procedures.inc"),
              encoding="latin-1") as f:
        for line in f:
            match = re.match(r"^l([0-9A-F]{8}) equ (\S+)", line)
            if match:
                procedures[match.group(2)] = int(match.group(1), 16)
    return procedures


def _read_implemented(asm_dir):
    with open(os.path.join(asm_dir, "native.asm"), encoding="latin-1") as f:
        native = f.read()
    return set(int(address, 16) for address in re.findall(
        r"call l([0-9A-F]{8}); Implemented in c\+\+ code", native))


def assert_lines(code, relocations):
    """(offset, size) of line numbers pushed for calls of _assert.

    Line numbers of assert differ from the original sources, a line number
    above 127 is pushed as a 32-bit immediate, others as 8-bit ones.
    """
    result = []
    for offset, target in relocations:
        if "_assert" not in target:
            continue
        # push line; push file; push expression; call [__imp__assert]
        position = offset - 2 - 10
        if position >= 2 and code[position - 2] == 0x6A:
            result.append((position - 1, 1))
        elif position >= 5 and code[position - 5] == 0x68:
            result.append((position - 4, 4))
    return result


def compare(bldmystery, work, modules, json_file):
    results = {}
    for module in modules:
        data = ModuleData(bldmystery, work, module)
        module_results = {}
        for name, address in sorted(
            data.procedures.items(), key=lambda item: item[1]
        ):
            if address not in data.implemented:
                continue
            module_results[name] = (address, _classify(data, name, address))
        results[module] = module_results
        _print_module_results(module, module_results)
    if json_file:
        with open(json_file, "w") as f:
            json.dump(results, f, indent=1, sort_keys=True)
    return 0


def _classify(data, name, address):
    """OK, LINES (line numbers of assert only), STACK (offsets of local
    variables only), FRAME (stack offsets and size of the frame), CODE or
    MISSING (not compiled)."""
    compiled = data.compiled(name)
    if compiled is None:
        return "MISSING"
    path, code, mask, relocations, relocations_mask = compiled
    original = data.original(address, len(code))
    differences = [
        i for i in range(len(code)) if not mask[i] and code[i] != original[i]
    ]
    if not differences:
        if any(not relocations_mask[i] and code[i] != original[i]
               for i in range(len(code))):
            return "LINES"
        return "OK"
    # The binary can be longer: line numbers of assert above 127 are 32-bit
    original = data.original(address, len(code) + 64)
    try:
        compiled_instrs, original_instrs = (
            _normalize_lines([i[1] for i in instrs])
            for instrs in _disassemble_pair(data, compiled, original))
    except DisassemblerNotFound:
        return "CODE"
    # The last instruction can be cut: jump tables of switch are at the end
    compiled_instrs = compiled_instrs[:-1]
    original_instrs = original_instrs[:len(compiled_instrs)]
    if compiled_instrs == original_instrs:
        return "LINES"
    if _normalize_stack(compiled_instrs) == _normalize_stack(
            original_instrs):
        return "STACK"
    if _normalize_frame(compiled_instrs) == _normalize_frame(
            original_instrs):
        return "FRAME"
    return "CODE"


def _normalize_lines(instrs):
    """Replace line numbers of assert: push line, push file, push
    expression, call _assert."""
    instrs = list(instrs)
    for i in range(len(instrs) - 3):
        if (
            re.match(r"^push -?(0x[0-9a-f]+|\d+)$", instrs[i]) and
            instrs[i + 1] == "push ADDR" and instrs[i + 2] == "push ADDR" and
            instrs[i + 3] == "call [ADDR]"
        ):
            instrs[i] = "push LINE"
    return instrs


RELOCATION_MARKER = 0x7EEEEEEE


def _disassemble_pair(data, compiled, original):
    """Instructions of the compiled and the original procedure, addresses
    of the binary and fields changed by the linker are written as ADDR."""
    path, code, mask, relocations, relocations_mask = compiled
    # Line numbers of assert are taken from the binary, fields changed by
    # the linker are marked: the binary can be shifted relative to them.
    merged = bytearray(
        original[i] if mask[i] and not relocations_mask[i] and
        i < len(original) else code[i] for i in range(len(code)))
    # Runs of more than two fields are jump tables of switch: data, they
    # are taken from the binary.
    marker = struct.pack("<I", RELOCATION_MARKER)
    start = None
    for i in range(len(code) + 1):
        if i < len(code) and relocations_mask[i]:
            if start is None:
                start = i
            continue
        if start is not None:
            for j in range(start, i):
                merged[j] = (
                    original[j] if i - start > 8 and j < len(original)
                    else marker[(j - start) % 4])
            start = None
    low, high = data.image_range()

    def addresses(text):
        def replace(match):
            value = int(match.group(0), 16)
            if value == RELOCATION_MARKER or low <= value < high:
                return "ADDR"
            return match.group(0)
        return re.sub(r"0x[0-9a-f]+", replace, text)

    return (
        [(offset, addresses(text))
         for offset, text in disassemble(bytes(merged))],
        [(offset, addresses(text))
         for offset, text in disassemble(original)],
    )


def _normalize_stack(instrs):
    return [re.sub(r"\[ebp ?- ?(0x[0-9a-f]+|\d+)\]", "[ebp-N]", _normalize(i))
            for i in instrs]


def _normalize_frame(instrs):
    instrs = _normalize_stack(instrs)
    if len(instrs) > 2 and (
        instrs[2].startswith("sub esp") or instrs[2] == "push ecx"
    ):
        instrs[2] = "FRAME"
    return instrs


def _normalize(instr):
    # Targets of direct calls and jumps are addresses of the binary
    return re.sub(r"^(call|j\w+) (0x[0-9a-f]+|-?\d+)$", r"\1 X", instr)


def _print_module_results(module, results):
    statuses = [status for address, status in results.values()]
    counts = ", ".join(
        "{} {}".format(status, statuses.count(status))
        for status in ("OK", "LINES", "STACK", "FRAME", "CODE", "MISSING")
        if statuses.count(status))
    print("== {}: {} implemented procedures: {}".format(
        module, len(results), counts))
    for name, (address, status) in results.items():
        if status not in ("OK", "LINES"):
            print("  {:7} 0x{:08X} {}".format(status, address, name))


# Disassembling

class DisassemblerNotFound(Exception):
    pass


def disassemble(code):
    """[(offset, instruction)] of 32-bit x86 code."""
    try:
        import capstone
    except ImportError:
        capstone = None
    if capstone is not None:
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        result = []
        offset = 0
        while offset < len(code):
            instrs = list(md.disasm(code[offset:], offset, count=1))
            if not instrs:
                result.append((offset, "db 0x{:02x}".format(code[offset])))
                offset += 1
                continue
            instr = instrs[0]
            text = "{} {}".format(instr.mnemonic, instr.op_str).strip()
            text = text.replace("dword ptr ", "").replace(
                "qword ptr ", "").replace("word ptr ", "").replace(
                    "byte ptr ", "")
            result.append((offset, text))
            offset += instr.size
        return result
    if shutil.which("ndisasm"):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(code)
            path = f.name
        try:
            output = subprocess.run(
                ["ndisasm", "-b32", path], capture_output=True,
                text=True).stdout
        finally:
            os.unlink(path)
        result = []
        for line in output.splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3:
                result.append((int(parts[0], 16), parts[2]))
        return result
    raise DisassemblerNotFound(
        "Install capstone ('pip install capstone') or ndisasm of NASM")


def diff(bldmystery, work, modules, names, max_lines):
    for name in names:
        found = False
        for module in modules:
            data = ModuleData(bldmystery, work, module)
            address = data.procedures.get(name)
            if address is None:
                continue
            compiled = data.compiled(name)
            if compiled is None:
                continue
            found = True
            path, code = compiled[:2]
            original = _original_procedure(data, address, len(code))
            compiled_instrs, original_instrs = _disassemble_pair(
                data, compiled, original)
            print("=== {} 0x{:08X} {} (compiled {} bytes, original {})".format(
                name, address, os.path.basename(path), len(code),
                len(original)))
            matcher = difflib.SequenceMatcher(
                None, [_normalize(i[1]) for i in compiled_instrs],
                [_normalize(i[1]) for i in original_instrs], autojunk=False)
            lines = 0
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    continue
                for offset, text in compiled_instrs[i1:i2]:
                    print("  - +{:04X} {}".format(offset, text))
                for offset, text in original_instrs[j1:j2]:
                    print("  + +{:04X} {}".format(offset, text))
                print("  ---")
                lines += (i2 - i1) + (j2 - j1) + 1
                if lines > max_lines:
                    print("  ...")
                    break
            if lines == 0:
                print("  identical instructions")
            break
        if not found:
            print("=== {}: not found".format(name))
    return 0


def _original_procedure(data, address, compiled_size):
    """Code of the binary up to the next procedure without padding."""
    following = [a for a in data.procedures.values() if a > address]
    end = min(following + [address + compiled_size + 64])
    code = data.original(address, end - address)
    size = len(code)
    while size > 0 and code[size - 1] in (0xCC, 0x90):
        size -= 1
    return code[:size]


def stack(bldmystery, work, modules, name):
    """Print local variables of the compiled procedure with offsets of the
    same variables in the binary found by matching instructions."""
    for module in modules:
        data = ModuleData(bldmystery, work, module)
        address = data.procedures.get(name)
        compiled = data.compiled(name) if address is not None else None
        if compiled is None:
            continue
        path, code = compiled[:2]
        original = data.original(address, len(code) + 64)
        compiled_instrs, original_instrs = (
            [i[1] for i in instrs]
            for instrs in _disassemble_pair(data, compiled, original))
        pairs = {}
        matcher = difflib.SequenceMatcher(
            None, _normalize_stack(compiled_instrs),
            _normalize_stack(original_instrs), autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag not in ("equal", "replace") or i2 - i1 != j2 - j1:
                continue
            for x, y in zip(compiled_instrs[i1:i2], original_instrs[j1:j2]):
                for p, q in zip(_ebp_offsets(x), _ebp_offsets(y)):
                    counts = pairs.setdefault(p, {})
                    counts[q] = counts.get(q, 0) + 1
        names = _listing_variables(os.path.splitext(path)[0] + ".asm", name)
        print("{} 0x{:08X}".format(name, address))
        print("  compiled  binary  variable")
        for offset in sorted(pairs, reverse=True):
            binary_offset = max(pairs[offset], key=pairs[offset].get)
            variable = names.get(offset, "")
            marker = "" if binary_offset == offset else "  <=="
            bucket_text = ""
            if variable and not variable.startswith("$"):
                bucket_text = " (bucket {})".format(
                    bucket(variable.split("$")[0].lstrip("_")))
            print("  {:8} {:7}  {}{}{}".format(
                offset, binary_offset, variable, bucket_text, marker))
        return 0
    print("{}: not found".format(name))
    return 1


def _ebp_offsets(instr):
    return [-int(x, 0) for x in re.findall(
        r"ebp ?- ?(0x[0-9a-f]+|\d+)\b", instr)]


def _listing_variables(listing, name):
    """{offset: name} of local variables of the procedure in the listing."""
    variables = {}
    if not os.path.exists(listing):
        return variables
    with open(listing, encoding="latin-1") as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        if line.startswith(name + "\tPROC") or line.startswith(
            name + " PROC"
        ):
            for previous in reversed(lines[max(0, i - 200):i]):
                match = re.match(r"^(\S+)\s*=\s*(-?\d+)", previous)
                if not match:
                    if previous.strip() and not previous.startswith(";"):
                        break
                    continue
                variables[int(match.group(2))] = match.group(1)
            break
    return variables


if __name__ == "__main__":
    sys.exit(main())
