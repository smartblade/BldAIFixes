"""Stack layout of local variables in Visual C++ 6.0, see stack-layout.md."""

NUM_BUCKETS = 16


def bucket(name):
    """Hash bucket of a local variable name, buckets are placed in order."""
    v = 0
    for ch in name:
        v = ((v << 2) + (v >> 4) + ord(ch)) & 0xFFFFFFFF
    return (v ^ (v >> 16)) % NUM_BUCKETS


def order_key(block_index, name, declaration_index):
    """Key of the order of a local variable in the stack frame.

    block_index is the index of the block of the variable in preorder
    (0 is the body of the procedure), declaration_index is the position
    of the declaration in the block. Variables sorted by the key are placed
    from higher to lower addresses.
    """
    return (block_index, bucket(name), -declaration_index)
