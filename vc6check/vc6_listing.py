"""Compiling test sources with cl.exe and reading local variables of listings.

cl.exe is run as the command in the VC6_CL environment variable ("cl" by
default), e.g. VC6_CL="wine CL.EXE" with WINEPATH set to VC98/Bin and
Common/MSDev98/Bin of Visual C++ 6.0.
"""
import os
import re
import shlex
import subprocess
import tempfile

LOCAL_REGEXP = re.compile(r'^(_\w+?\$\d*|\$T\d+)\s*=\s*(-?\d+)')


def compile_listing(source, options=("/Od", "/Zp4")):
    """Compile C++ source text, return the text of the listing (/FAs)."""
    cl = shlex.split(os.environ.get("VC6_CL", "cl"))
    with tempfile.TemporaryDirectory() as tmp_dir:
        with open(os.path.join(tmp_dir, "t.cpp"), "w") as f:
            f.write(source)
        result = subprocess.run(
            cl + ["/nologo", "/c", "/FAs"] + list(options) + ["t.cpp"],
            cwd=tmp_dir, capture_output=True, text=True)
        listing = os.path.join(tmp_dir, "t.asm")
        if not os.path.exists(listing):
            raise RuntimeError(result.stdout + result.stderr)
        with open(listing, encoding="latin-1") as f:
            return f.read()


def read_procedures(listing):
    """Yield (procedure, {variable: offset}, source line numbers)."""
    lines = listing.split("\n")
    variables = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        match = LOCAL_REGEXP.match(line)
        if match:
            variables[match.group(1)] = int(match.group(2))
        if " PROC NEAR" in line:
            name = line.split()[0]
            source_lines = []
            index += 1
            while " ENDP" not in lines[index]:
                match = re.match(r'^; (\d+)\s+:', lines[index])
                if match:
                    source_lines.append(int(match.group(1)))
                index += 1
            yield name, variables, source_lines
            variables = {}
        index += 1


def variable_name(listing_name):
    """Name of a variable in the source by its name in the listing."""
    return re.sub(r'\$\d*$', '', listing_name)[1:]
