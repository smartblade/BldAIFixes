# Changes of a pull request branch

Changes of the branch of a pull request are made in separate commits in
the following order:

1. Style fixes applied by `tools/style.py` of master, one rule per commit:

   ```
   python tools/style.py fix --rule RULE
   ```

2. Other rules of the style guide (`docs/code-style.md` of master), one
   rule per commit.
3. Significant differences from the code compiled by VC6, which change
   the logic of the code.
4. Insignificant differences from the code compiled by VC6, except the
   layout of the stack.
5. The layout of the stack, in one commit.
6. The remaining changes which make the code match the output of
   recompile.
