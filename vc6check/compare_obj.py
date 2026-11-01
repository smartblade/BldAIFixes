"""Compare procedures compiled to COFF object files with the original binary.

Bytes of each procedure in an object file are compared with bytes at the
procedure address in raw.txt (the disassembly of the original binary).
Bytes changed by the linker (relocations) are not compared.
"""
import argparse
import os
import re
import struct
import sys

# Module name: [(mangled name, address in the original binary)]
PROCEDURES = {
    "BBLibc.dll": [
        ("?GetnOpenedFiles@B_IDataFile@@SAHXZ", 0x1000100F),
        ("?Seek@B_IDataFile@@QAEJJH@Z", 0x100018A6),
        ("?Read@B_IDataFile@@QAEXPAXI@Z", 0x10001A33),
        ("??0B_Name@@QAE@PBD@Z", 0x10003337),
        ("?OutputWin32Error@@YAXPBD@Z", 0x1002A590),
    ],
    "Blade.exe": [
        (
            "?CollectSectorsAtPoint@B_OctantNode@@"
            "UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z",
            0x00452388,
        ),
        (
            "?CollectSectorsInBox@B_OctantNode@@"
            "UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z",
            0x00452845,
        ),
        (
            "?FindSectorsAtPoint@B_OctTree@@"
            "UBEXABVB_Vector@@PAVB_OctTreeSectorsList@@@Z",
            0x00453067,
        ),
    ],
}

IMAGE_SYM_DTYPE_FUNCTION = 0x20
IMAGE_SCN_LNK_COMDAT = 0x00001000
# Sizes of fields changed by i386 relocations
RELOCATION_SIZES = {
    0x0006: 4,  # IMAGE_REL_I386_DIR32
    0x0007: 4,  # IMAGE_REL_I386_DIR32NB
    0x000A: 2,  # IMAGE_REL_I386_SECTION
    0x000B: 4,  # IMAGE_REL_I386_SECREL
    0x0014: 4,  # IMAGE_REL_I386_REL32
}

raw_line_regexp = re.compile(r'^(?P<addr>[0-9A-F]{8}): (?P<bytes>[0-9A-F]+)\s')
export_regexp = re.compile(r'^\* Export: (?P<name>[^,]+),')


class Section:
    def __init__(self, data, header):
        (
            name, _, _, size, raw_ptr, relocs_ptr, _, n_relocs, _,
            self.characteristics,
        ) = struct.unpack("<8sIIIIIIHHI", header)
        self.name = name.rstrip(b"\0").decode("latin-1")
        self.data = data[raw_ptr:raw_ptr + size]
        self.relocations = []
        for i in range(n_relocs):
            offset = relocs_ptr + i * 10
            addr, symbol_index, reloc_type = struct.unpack(
                "<IIH", data[offset:offset + 10])
            self.relocations.append((addr, symbol_index, reloc_type))


class Symbol:
    def __init__(self, name, value, section_number, sym_type):
        self.name = name
        self.value = value
        self.section_number = section_number
        self.type = sym_type


class ObjFile:
    def __init__(self, file_name):
        with open(file_name, "rb") as f:
            data = f.read()
        (
            machine, n_sections, _, symbols_ptr, n_symbols, optional_size, _,
        ) = struct.unpack("<HHIIIHH", data[:20])
        if machine != 0x014C:
            raise Exception("{} is not i386 object file".format(file_name))
        self.file_name = file_name
        self.sections = []
        offset = 20 + optional_size
        for i in range(n_sections):
            header = data[offset + i * 40:offset + (i + 1) * 40]
            self.sections.append(Section(data, header))
        self.symbols = []
        # Symbol by index in symbol table (with auxiliary records)
        self.symbols_by_index = {}
        strings_ptr = symbols_ptr + n_symbols * 18
        i = 0
        while i < n_symbols:
            offset = symbols_ptr + i * 18
            name, value, section_number, sym_type, _, n_aux = struct.unpack(
                "<8sIhHBB", data[offset:offset + 18])
            if name[:4] == b"\0\0\0\0":
                name_ptr = strings_ptr + struct.unpack("<I", name[4:])[0]
                name = data[name_ptr:data.index(b"\0", name_ptr)]
            else:
                name = name.rstrip(b"\0")
            symbol = Symbol(
                name.decode("latin-1"), value, section_number, sym_type)
            self.symbols.append(symbol)
            self.symbols_by_index[i] = symbol
            i += 1 + n_aux

    def functions(self):
        for symbol in self.symbols:
            if (
                symbol.type == IMAGE_SYM_DTYPE_FUNCTION and
                symbol.section_number > 0
            ):
                yield symbol

    def get_function_code(self, symbol):
        section = self.sections[symbol.section_number - 1]
        end = len(section.data)
        if not section.characteristics & IMAGE_SCN_LNK_COMDAT:
            for other in self.functions():
                if (
                    other.section_number == symbol.section_number and
                    symbol.value < other.value < end
                ):
                    end = other.value
        code = section.data[symbol.value:end]
        mask = [False] * len(code)
        relocations = []
        for addr, symbol_index, reloc_type in section.relocations:
            if not symbol.value <= addr < end:
                continue
            size = RELOCATION_SIZES.get(reloc_type, 4)
            for i in range(addr, addr + size):
                if i < end:
                    mask[i - symbol.value] = True
            relocations.append(
                (addr - symbol.value, self._describe_symbol(symbol_index)))
        return code, mask, relocations

    def _describe_symbol(self, symbol_index):
        target = self.symbols_by_index.get(symbol_index)
        if target is None:
            return "symbol {}".format(symbol_index)
        if target.section_number > 0:
            section = self.sections[target.section_number - 1].name
        elif target.section_number == 0:
            section = "external"
        else:
            section = "absolute"
        return "{} ({})".format(target.name, section)


def read_raw(file_name):
    memory = {}
    exports = {}
    export = None
    with open(file_name, encoding="cp1251", errors="replace") as f:
        for line in f:
            match = export_regexp.match(line)
            if match:
                export = match.group("name")
                continue
            match = raw_line_regexp.match(line)
            if not match:
                continue
            addr = int(match.group("addr"), 16)
            if export is not None:
                exports[export] = addr
                export = None
            hex_bytes = match.group("bytes")
            for i in range(0, len(hex_bytes), 2):
                memory[addr + i // 2] = int(hex_bytes[i:i + 2], 16)
    return memory, exports


def format_bytes(code, mask, start, end):
    return " ".join(
        ".." if mask[i] else "{:02X}".format(code[i])
        for i in range(start, end))


def compare(name, addr, code, mask, relocations, memory, show_relocations):
    original = bytes(memory.get(addr + i, 0x100) & 0xFF for i in range(len(code)))
    missing = [i for i in range(len(code)) if addr + i not in memory]
    differences = [
        i for i in range(len(code))
        if not mask[i] and (addr + i not in memory or code[i] != original[i])
    ]
    status = "OK" if not differences else "MISMATCH"
    print("{} {} at 0x{:08X}, {} bytes, {} relocated bytes not compared".format(
        status, name, addr, len(code), sum(mask)))
    if missing:
        print("    {} bytes are missing in raw.txt".format(len(missing)))
    if differences:
        rows = sorted(set(i // 16 for i in differences))
        for row in rows:
            start = row * 16
            end = min(start + 16, len(code))
            no_mask = [False] * len(code)
            print("    +{:04X} compiled: {}".format(
                start, format_bytes(code, mask, start, end)))
            print("    +{:04X} original: {}".format(
                start, format_bytes(original, no_mask, start, end)))
    if show_relocations:
        for offset, target in relocations:
            print("    +{:04X} -> {}".format(offset, target))
    return not differences


class Memory:
    """Bytes of the original binary for searching of procedures."""

    def __init__(self, memory):
        self._base = min(memory)
        end = max(memory) + 1
        data = bytearray(end - self._base)
        for addr, value in memory.items():
            data[addr - self._base] = value
        self._data = bytes(data)

    def find(self, code, mask):
        """Return addresses of all matches of code, masked bytes match any."""
        anchor_start, anchor_end = _longest_unmasked_run(mask)
        if anchor_end - anchor_start < 4:
            return []
        anchor = code[anchor_start:anchor_end]
        addresses = []
        pos = self._data.find(anchor)
        while pos >= 0:
            start = pos - anchor_start
            if start >= 0 and self._matches(start, code, mask):
                addresses.append(self._base + start)
            pos = self._data.find(anchor, pos + 1)
        return addresses

    def _matches(self, start, code, mask):
        data = self._data[start:start + len(code)]
        if len(data) != len(code):
            return False
        return all(mask[i] or data[i] == code[i] for i in range(len(code)))


def _longest_unmasked_run(mask, max_length=32):
    best = (0, 0)
    start = None
    for i in range(len(mask) + 1):
        if i < len(mask) and not mask[i]:
            if start is None:
                start = i
            if i + 1 - start > best[1] - best[0]:
                best = (start, i + 1)
            if best[1] - best[0] >= max_length:
                break
        else:
            start = None
    return best


def search(obj_file_names, memory):
    """Search all procedures of object files in the original binary."""
    memory = Memory(memory)
    found_count = 0
    total_count = 0
    for obj_file_name in _expand_directories(obj_file_names):
        obj_file = ObjFile(obj_file_name)
        for symbol in obj_file.functions():
            code, mask, _ = obj_file.get_function_code(symbol)
            total_count += 1
            addresses = memory.find(code, mask)
            if len(addresses) == 1:
                found_count += 1
                status = "FOUND"
            elif addresses:
                found_count += 1
                status = "MULTIPLE"
            else:
                status = "NOT FOUND"
            print("{} {} ({}, {} bytes){}".format(
                status, symbol.name, os.path.basename(obj_file_name),
                len(code),
                "".join(" 0x{:08X}".format(a) for a in addresses)))
    print("Found {} of {} procedures".format(found_count, total_count))
    return found_count == total_count


def _expand_directories(file_names):
    for file_name in file_names:
        if os.path.isdir(file_name):
            for name in sorted(os.listdir(file_name)):
                if name.lower().endswith(".obj"):
                    yield os.path.join(file_name, name)
        else:
            yield file_name


def read_module_name(raw_file_name):
    module_file_name = os.path.join(
        os.path.dirname(os.path.abspath(raw_file_name)), "module.txt")
    with open(module_file_name) as f:
        return f.readline().strip()


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "--raw", required=True, help="raw.txt of the original binary")
    arg_parser.add_argument(
        "--all", action="store_true",
        help="compare all exported procedures found in object files")
    arg_parser.add_argument(
        "--relocs", action="store_true",
        help="print targets of relocations: called procedures, variables "
        "and constants (float literals are __real@... symbols)")
    arg_parser.add_argument(
        "--search", action="store_true",
        help="search all procedures of object files in the original binary "
        "instead of comparing at known addresses")
    arg_parser.add_argument(
        "obj_files", nargs="+",
        help="object files (with --search also directories of object files)")
    args = arg_parser.parse_args()
    memory, exports = read_raw(args.raw)
    if args.search:
        return 0 if search(args.obj_files, memory) else 1
    module_procedures = PROCEDURES.get(read_module_name(args.raw), [])
    procedures = dict(module_procedures)
    if args.all:
        procedures.update(exports)
    found = set()
    all_match = True
    for obj_file_name in args.obj_files:
        obj_file = ObjFile(obj_file_name)
        for symbol in obj_file.functions():
            addr = procedures.get(symbol.name)
            if addr is None or symbol.name in found:
                continue
            found.add(symbol.name)
            code, mask, relocations = obj_file.get_function_code(symbol)
            all_match &= compare(
                symbol.name, addr, code, mask, relocations, memory,
                args.relocs)
    for name, addr in module_procedures:
        if name not in found:
            print("NOT FOUND {} (0x{:08X}) in object files".format(name, addr))
            all_match = False
    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
