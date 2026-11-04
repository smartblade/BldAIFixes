# Stack layout of local variables in Visual C++ 6.0

Rules of placing local variables in the stack frame by `cl.exe` of
Visual C++ 6.0 without optimizations (`/Od`). They are derived from test
sources compiled with `cl.exe` 12.00.8804 (Visual C++ 6.0 SP5/SP6) and
checked on BldMystery sources.

## Rules

1. The order of declarations inside one block doesn't matter:
   `int a; int b; int c;` and `int c; int b; int a;` give the same offsets.
2. Blocks are placed in preorder. All variables of the body of the
   procedure are placed first, including variables declared after nested
   blocks, then the nested blocks in the order of the source, each block
   followed by its own nested blocks. A variable declared in the
   initialization of `for` belongs to the enclosing block. Sibling blocks
   don't share stack memory.
3. Inside a block variables are ordered by the hash of their names: hash
   buckets are placed in ascending order, a variable declared later is
   placed first inside a bucket. There are 16 buckets:

   ```python
   def bucket(name):
       v = 0
       for ch in name:
           v = ((v << 2) + (v >> 4) + ord(ch)) & 0xFFFFFFFF
       return (v ^ (v >> 16)) & 15
   ```

4. Each variable is placed at the next lower address, its size is rounded
   up to 4 bytes. `double` variables are not aligned to 8 bytes.
5. Variables that are never used get no stack memory.
6. `this` saved in the stack frame is placed after all local variables.
   Temporaries of the compiler (`$T` in listings) and local variables of
   inlined procedures are placed after the variables of the source.

Example of rules 2 and 3 (offsets of the listing in the comments):

```cpp
void f()
{
    int a;              // -4,  bucket 1
    {
        int b;          // -12, nested block
        double d;       // -20, nested block
        use(&b);
        use(&d);
    }
    int c;              // -8,  body of the procedure, bucket 3
    use(&a);
    use(&c);
}
```

## Consequences for recompiled code

The offsets of the original binary restrict the declarations:

- A variable placed above a variable of the body of the procedure is
  declared in the body too, even if it is used only in a nested block. In
  `B_OctTreeSectorsList::BuildSurfaceCache` (`0x0045327B`) `distance`
  (`-8`) is above `i` (`-12`), so it is declared at the start of the
  procedure, not inside the loop where it is used.
- The names of the variables of one block must have buckets in the order
  of their offsets, a name with a wrong bucket changes the layout. For
  example `current_surface` (bucket 8) is placed below `distance`
  (bucket 2) of the same block, although it is declared earlier.
- Variables of one block in the same bucket are declared in the reverse
  order of their offsets.

## Checks

- The hash function is derived from the order of 1466 names and checked on
  600 random names of 1 to 31 characters (letters, digits and `_`), all
  buckets match.
- All BBLibc sources (21 files) and 41 other files of BldMystery are
  compiled, the order of the local variables in the listings (`/FAs`) is
  compared with the rules: 63 procedures with two or more local variables
  match, including `operator >>` of `B_World` with 13 variables in
  8 nested blocks and variables of the same names in different blocks.
- `BuildSurfaceCache` with `distance` declared in the body of the
  procedure has the same stack frame as in `Blade.exe` (built with
  12.00.8799), so the rules are the same for both builds at least in this
  case.
