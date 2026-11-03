# libjpeg in BBLibc.dll

`BBLibc.dll` contains IJG libjpeg 6b (`100096A0`-`1002698F`, 46 C object
files of the Rich header). Its procedures are declared in
`src/BBLibc/libjpeg`: `jpeglib.h` declares types used by signatures and
each `.c` file declares procedures of one source file of libjpeg 6b with
their addresses. Bodies are empty, BldRecompile converts them.

## How addresses were found

- Sources of libjpeg 6b were taken from the PyPI package `jpeglib` 1.0.2
  (`src/jpeglib/cjpeglib/6b`). Procedures compiled with the default
  options of `jmorecfg.h` are counted: 335 procedures of 46 files.
- With `/Od` every procedure starts with `push ebp; mov ebp, esp`. Starts
  are taken from the disassembly and from the bytes after `switch` jump
  tables, which the disassembler shows as data: 335 starts.
- Object files are linked in alphabetical order of file names (the order
  of files in the Visual C++ project), each block of code between `int 3`
  gaps starts with a new file and numbers of procedures of files match the
  blocks.
- Visual C++ 6 places procedures of a file in the order in which it
  compiles them, not in the order of definitions:
  - global procedures are compiled at their definitions;
  - static procedures are compiled when they are referenced: a static
    procedure referenced by a compiled procedure is compiled right after
    it (depth first, in the order of definitions) if it is defined before
    the referencing procedure, otherwise at its definition;
  - static procedures referenced by procedures defined after them and not
    compiled yet are compiled at the end of the file.
- The result agrees with all 440 direct calls between libjpeg procedures:
  each call target is called in the source of the caller (25 calls are
  made by macros of `jdhuff.h`, which isn't in the package).

## Limitations

- `jpeglib.h` isn't the original header: structures are declared without
  fields, enumerations are `int` and `jpeg_marker_parser_method` and
  `ODITHER_MATRIX_PTR` are simplified. Structures are used without the
  `struct` keyword in signatures, like in C++.
- Procedures in the `.c` files are in the order of their addresses, which
  differs from the original files as described above.
- `boolean` is `unsigned char` (`jconfig.vc`): procedures return it in
  `al`.
