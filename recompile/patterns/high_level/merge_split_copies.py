import data_types
import expressions
import instructions


def merge_split_copies(instrs, double_offsets=()):
    """Merge copies of halves of 8-byte stack variables.

    Doubles are copied with two 32-bit moves:

        STACKVAR(-232, 4) = STACKVAR(-16, 4);
        STACKVAR(-228, 4) = STACKVAR(-12, 4);

    Merge them to 'STACKVAR(-232, 8) = STACKVAR(-16, 8)' if the source or
    the destination is accessed as 8-byte stack variable elsewhere, e.g. a
    field of a local object copied to an argument of an inlined method.
    Zero is stored to a double with two 32-bit moves too, e.g. by an
    inlined 'B_Vector()': 'STACKVAR(-24, 8) = 0.0' if the destination is
    accessed as 8-byte stack variable.
    double_offsets are offsets of double fields of local objects known from
    the analysis. Copies are merged repeatedly: a merged destination may be
    the source of other copy, e.g. a field copied to a temporary and then to
    a field of other object.
    """
    while True:
        qwords = set(double_offsets)

        def on_visit(e, **kwargs):
            if (
                isinstance(e, expressions.intermediate.Stackvar) and
                e.size == 8
            ):
                qwords.add(e.offset)

        for instr in instrs:
            instr.visit(on_visit)
        new_instrs = _merge_block(instrs, qwords)
        if _count_instructions(new_instrs) == _count_instructions(instrs):
            return new_instrs
        instrs = new_instrs


def _count_instructions(block):
    count = 0
    for instr in block:
        count += 1
        for attr in ("if_block", "else_block", "block", "instructions"):
            sub = getattr(instr, attr, None)
            if isinstance(sub, list):
                count += _count_instructions(sub)
    return count


def _merge_block(block, qwords):
    new_block = []
    i = 0
    while i < len(block):
        instr = _merge_nested(block[i], qwords)
        if i + 1 < len(block):
            merged = _try_merge(instr, block[i + 1], qwords)
            if merged is not None:
                new_block.append(merged)
                i += 2
                continue
        new_block.append(instr)
        i += 1
    return new_block


def _try_merge(low, high, qwords):
    zero = _try_merge_zero(low, high, qwords)
    if zero is not None:
        return zero
    low_halves = _stackvar_copy(low)
    high_halves = _stackvar_copy(high)
    if low_halves is None or high_halves is None:
        return None
    low_dst, low_src = low_halves
    high_dst, high_src = high_halves
    if high_dst != low_dst + 4 or high_src != low_src + 4:
        return None
    if low_src not in qwords and low_dst not in qwords:
        return None
    # Copies of overlapping halves are not a copy of 8 bytes
    if abs(low_dst - low_src) < 8:
        return None
    return instructions.Assignment(
        expressions.intermediate.Stackvar(low_dst, 8),
        expressions.intermediate.Stackvar(low_src, 8),
    )


def _try_merge_zero(low, high, qwords):
    low_dst = _stackvar_zero(low)
    high_dst = _stackvar_zero(high)
    if low_dst is None or high_dst != low_dst + 4 or low_dst not in qwords:
        return None
    return instructions.Assignment(
        expressions.intermediate.Stackvar(low_dst, 8),
        expressions.Constant(data_types.Double(), 0.0),
    )


def _stackvar_zero(instr):
    """Offset of 'STACKVAR(offset, 4) = 0', None for other instructions."""
    if not isinstance(instr, instructions.Assignment):
        return None
    dst, src = instr.dst, instr.src
    if not isinstance(dst, expressions.intermediate.Stackvar) or dst.size != 4:
        return None
    if not isinstance(src, expressions.Constant) or src.value != 0:
        return None
    return dst.offset


def _stackvar_copy(instr):
    if not isinstance(instr, instructions.Assignment):
        return None
    dst, src = instr.dst, instr.src
    for e in (dst, src):
        if not isinstance(e, expressions.intermediate.Stackvar):
            return None
        if e.size != 4:
            return None
    return dst.offset, src.offset


def _merge_nested(instr, qwords):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _merge_block(else_block, qwords)
        return instructions.IfInstruction(
            instr.if_clause, _merge_block(instr.if_block, qwords), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _merge_block(instr.block, qwords))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _merge_block(instr.instructions, qwords))
    if isinstance(instr, instructions.Switch):
        for label, block in instr.blocks_dict.items():
            instr.blocks_dict[label] = _merge_block(block, qwords)
    return instr
