# Changes of a pull request branch

Changes of the branch of a pull request are made in separate commits in
the following order:

1. The layout of the files, in one commit:

   - procedures and variables are defined in the source file of the
     object file containing them in the binary, the boundaries of object
     files are found by 'int 3' padding to addresses aligned to 16, the
     order of procedures and the table of dynamic initializers;
   - methods outside of the object file of their class (compiled as
     separate COMDAT sections after the object files using them) are
     inline methods defined in the headers;
   - procedures and variables used by other source files are declared in
     the header of their source file;
   - `src/Blade/bld_misc_funcs.cpp` lists the ranges of the new source
     files with their names:

     ```
     /* File:                  Physics/ContactList.cpp */
     /* Begin of file:         0x004ABD40 */
     /* End of file:           0x004ACB70 */
     ```

     A range ends at the start of the next object file: after 'int 3'
     padding or at its first dynamic initializer.

2. Style fixes applied by `tools/style.py` of master, one rule per commit:

   ```
   python tools/style.py fix --rule RULE
   ```

3. Other rules of the style guide (`docs/code-style.md` of master), one
   rule per commit.
4. Significant differences from the code compiled by VC6, which change
   the logic of the code.
5. Insignificant differences from the code compiled by VC6, except the
   layout of the stack.
6. The layout of the stack, in one commit.
7. The remaining changes which make the code match the output of
   recompile.
