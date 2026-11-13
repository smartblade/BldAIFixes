# Comparing BldMystery sources compiled with Visual C++ 6.0

`build.bat` compiles sources of
[BldMystery](https://github.com/smartblade/BldMystery) with Visual C++ 6.0
and `compare_obj.py` compares compiled procedures with the original
`BBLibc.dll` and `Blade.exe` byte by byte (using `src/BBLibc/asm/raw.txt`
and `src/Blade/asm/raw.txt` of BldMystery). Bytes changed by the linker
(addresses of called procedures, global variables and constants) are not
compared.

Compared procedures of `BBLibc.dll`:

| Address | Procedure | Characteristic code |
|---|---|---|
| `0x1000100F` | `B_IDataFile::GetnOpenedFiles` | trivial static method |
| `0x100018A6` | `B_IDataFile::Seek` | `switch`, inlined method |
| `0x10001A33` | `B_IDataFile::Read` | loop, `memcpy` |
| `0x10003337` | `B_Name::B_Name(const char *)` | constructor, `new`, `strlen` |
| `0x1002A590` | `OutputWin32Error` | WinAPI calls, `cdecl` |

Compared procedures of `Blade.exe` (`src/BWorld/OctTree.cpp` of BldMystery
pull request 7):

| Address | Procedure |
|---|---|
| `0x00452388` | `B_OctantNode::CollectSectorsAtPoint` |
| `0x00452845` | `B_OctantNode::CollectSectorsInBox` |
| `0x00453067` | `B_OctTree::FindSectorsAtPoint` |

`OctTree.cpp` is compiled three times: as is (`static double` constants),
with `static const double` constants and with literals instead of the
constants (`make_octtree_variants.py` makes the variants). For these
procedures targets of relocations are printed too: float literals of the
compiler are `__real@...` symbols in `.rdata`, `static double` variables
are in `.data`. In the original `Blade.exe` the constants are read from
`.rdata` and `-10.0` is a separate constant, see section 10 of
`docs/BldMystery-pull-7-review.md` in branch `claude/blade-single-procedure`.

`vc6compare.py` compares all implemented procedures of the three modules,
see [All implemented procedures](#all-implemented-procedures).

Rules of placing local variables in the stack frame by Visual C++ 6.0 are
described in [stack-layout.md](stack-layout.md).
Copies of inline functions, limits of their expansion and other signs of
inline functions in the code of Visual C++ 6.0 are described in
[inline-functions.md](inline-functions.md), `check_inline_limit.py` shows
the limits of expansion.

## Usage

Requirements: Visual C++ 6.0 (`cl.exe` version 12.00, the original binaries
are compiled with build 12.00.8799, Visual C++ 6.0 SP4, according to the Rich
header of `BBLibc.dll`, `build.bat` warns about other builds), Python 3 and a
checkout of BldMystery (pull request 7 for `Blade.exe`, without
`src/BWorld/OctTree.cpp` only `BBLibc.dll` is compared).

```bat
"C:\Program Files\Microsoft Visual Studio\VC98\Bin\VCVARS32.BAT"
vc6check\build.bat C:\path\to\BldMystery
```

Default compiler options are `/Zp4 /MD /Od /Ob1 /Gd /W3`, they can be
changed with `CFLAGS`, for example:

```bat
set CFLAGS=/Zp4 /MD /Od /Gd /W3
vc6check\build.bat C:\path\to\BldMystery
```

`COMPARE_FLAGS=--all` compares all exported procedures found in the
compiled object files, not only the procedures above, `--relocs` prints
targets of relocations.

`NDEBUG` is not defined: asserts are enabled, the original binaries call
`_assert`.

Output for each procedure is `OK` or `MISMATCH` with differing rows of
bytes (`..` marks bytes changed by the linker). The format, as produced
for hand-made object files with `GetnOpenedFiles` (the second one with
changed code):

```
OK ?GetnOpenedFiles@B_IDataFile@@SAHXZ at 0x1000100F, 10 bytes, 4 relocated bytes not compared
MISMATCH ?GetnOpenedFiles@B_IDataFile@@SAHXZ at 0x1000100F, 10 bytes, 0 relocated bytes not compared
    +0000 compiled: 55 8B EC 33 C0 90 90 90 90 5D
    +0000 original: 55 8B EC A1 FC 9E 04 10 5D C3
```

The script exits with code 1 if a procedure does not match or is not found.

## All implemented procedures

`vc6compare.py` compiles all sources of `Blade.exe`, `BBLibc.dll` and
`rOpenGL.dll` of a BldMystery checkout and compares every procedure marked
as implemented in C++ in `native.asm` (`call lXXXXXXXX; Implemented in c++
code`) with the binary (`raw.txt`). It is written in Python and runs on
Windows (command prompt or Git Bash) and on Linux or macOS with Wine.

Requirements: Python 3, Visual C++ 6.0 and, for the instruction
differences and the classification of mismatches, the `capstone` package
(`pip install capstone`) or `ndisasm` of NASM.

On Windows the compiler is `cl` of the environment of `VCVARS32.BAT`. Git
Bash started from the command prompt after `VCVARS32.BAT` inherits it:

```bat
"C:\Program Files\Microsoft Visual Studio\VC98\Bin\VCVARS32.BAT"
python vc6check\vc6compare.py build C:\path\to\BldMystery C:\path\to\work
python vc6check\vc6compare.py compare C:\path\to\BldMystery C:\path\to\work
```

```sh
# Git Bash started from the same command prompt
python vc6check/vc6compare.py build /c/path/to/BldMystery /c/path/to/work
```

Another compiler executable is set by `VC6_CL`, e.g.
`VC6_CL="C:\VC6\VC98\Bin\CL.EXE"`. With Wine `VC6_CL` runs `CL.EXE` by
`wine`, the paths of the sources are passed as `Z:` paths, `INCLUDE` holds
the include directory of Visual C++ 6.0:

```sh
VC=/path/to/vc6   # the directory with VC98 and Common
export VC6_CL="wine CL.EXE"
export WINEPATH="Z:$VC/VC98/Bin;Z:$VC/Common/MSDev98/Bin"
export INCLUDE="Z:$VC/VC98/Include"
python3 vc6check/vc6compare.py build ~/BldMystery /tmp/vc6work
python3 vc6check/vc6compare.py compare ~/BldMystery /tmp/vc6work
```

`build BLDMYSTERY WORK` copies `src` of BldMystery to `WORK/src` and
patches the copy for Visual C++ 6.0 (`PATCHES` of the script, each patch
not applied is printed):

- `<assert.h>` of Visual C++ 6.0 is used instead of `bld_assert.h`, like
  in the original binaries (calls of `_assert` of `msvcrt.dll`),
- variables declared by `for` are in the enclosing block in Visual C++ 6.0:
  the second loop of the block doesn't declare `i` again (`array.h`,
  `App.cpp`),
- the base class template of `B_SharedPtrArray` has its argument,
- `WinClock.cpp` declares the intrinsics instead of `<intrin.h>`.

Then it compiles the sources of each module (`MODULES` of the script) in
parallel to `WORK/obj/MODULE` with the options of the original build
`/c /MD /Od /Ob1 /Oi /Zp4 /GR- /DBLD_NATIVE /Doverride= /FAs` (and
`/DBBLIBC_LIB_EXPORT=` for `BBLibc.dll` like in `BBLibc.vcproj`;
`BoundingBox.cpp`, `Matrix.cpp`, `Plane.cpp` and `Vector.cpp` of
`AnalyticGeometry` are compiled for `BBLibc.dll` too), listings are
written next to the object
files. `--module` and `--file FILE` (repeatable, relative to `src`)
compile a part of the sources quickly.

`compare BLDMYSTERY WORK` prints the number of procedures of each module in
the categories below and lists the procedures that do not match.
`--json FILE` writes `{module: {procedure: [address, category]}}`.

| Category | Meaning |
|---|---|
| `OK` | identical (except bytes changed by the linker) |
| `LINES` | only line numbers of `assert` differ (an 8-bit `push` for lines below 128) |
| `STACK` | only offsets of local variables in the stack frame differ |
| `FRAME` | offsets of local variables and the size of the frame differ |
| `CODE` | the instructions differ |
| `MISSING` | the procedure is not found in the compiled object files |

`diff BLDMYSTERY WORK PROCEDURE...` prints the differing instructions of
procedures (mangled names) of the compiled code (`-`) and the binary
(`+`), targets of calls and jumps are not compared. `stack BLDMYSTERY WORK
PROCEDURE` prints offsets of local variables of the compiled procedure,
the offsets of the same variables in the binary (matched by instructions)
and the hash buckets of their names (see [stack-layout.md](stack-layout.md));
`<==` marks variables placed elsewhere in the binary:

```
?Build@B_OctTree@@QAEXABVB_Map@@N@Z 0x00451A21
  compiled  binary  variable
        -8      -8  _min_z$ (bucket 0)
       -16     -16  _max_x$ (bucket 4)
       ...
```

## libjpeg 6b

`BBLibc.dll` contains IJG libjpeg 6b (strings `6b  27-Mar-1998` and
`Copyright (C) 1998, Thomas G. Lane`) at `100096A0`-`1002698F` (see
`docs/BBLibc-object-map.md` in branch `claude/bblibc-object-map`).
`build_libjpeg.bat` compiles the library files of libjpeg 6b (`LIBOBJECTS`
of `makefile.vc` with the `jmemnobs` memory manager, 47 files; the Rich
header of `BBLibc.dll` counts 46 C objects) with `jconfig.vc` as
`jconfig.h` and searches each compiled procedure in `BBLibc.dll`:

```bat
vc6check\build_libjpeg.bat C:\path\to\BldMystery [C:\path\to\jpeg-6b]
```

Without the path to jpeg-6b sources `jpegsrc.v6b.tar.gz` is downloaded from
<https://www.ijg.org/files/> with `curl` and unpacked with `tar` of
Windows 10. The default compiler options are the same as for BBLibc
(`/Zp4 /MD /Od /Ob1 /Gd /W3`, set `CFLAGS` to try others, for example
without `/Zp4`).

libjpeg procedures are not exported, so `compare_obj.py --search` looks for
each procedure of the object files in the whole binary (relocated bytes
match any bytes) and prints `FOUND` with the address, `MULTIPLE` with all
addresses or `NOT FOUND`. The addresses also show the order of libjpeg
object files in the link and which files were linked (for example which
`jmem*.c` memory manager).
