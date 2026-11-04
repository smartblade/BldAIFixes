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

Rules of placing local variables in the stack frame by Visual C++ 6.0 are
described in [stack-layout.md](stack-layout.md).
Copies of inline functions compiled by Visual C++ 6.0 are described in
[inline-functions.md](inline-functions.md).

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
