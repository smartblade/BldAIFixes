"""Stack layout of local variables in Visual C++ 6.0.

See vc6check/stack-layout.md in branch claude/vc6-compare: variables of a
block are placed in the order of hash buckets of their names, a variable
declared later is placed first inside a bucket.
"""

NUM_BUCKETS = 16


def bucket(name):
    """Hash bucket of a local variable name, buckets are placed in order."""
    v = 0
    for ch in name:
        v = ((v << 2) + (v >> 4) + ord(ch)) & 0xFFFFFFFF
    return (v ^ (v >> 16)) % NUM_BUCKETS
