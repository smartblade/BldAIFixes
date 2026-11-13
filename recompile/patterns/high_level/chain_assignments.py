import data_types
import expressions
import instructions


def chain_assignments(procedure):
    """Restore chained assignments of objects of classes.

    'a = x; b = a;' is restored as 'b = a = x;' if a and b are objects of
    classes: Visual C++ 6.0 copies x to a and then a to b for both, e.g.
    'this->linearImpulse = this->angularImpulse = zero;'. Assignments of
    scalars are not chained: the chained one doesn't read a again.
    """
    return procedure.copy(instrs=_chain_block(list(procedure.instructions)))


def _chain_block(block):
    new_block = []
    for instr in block:
        instr = _chain_nested(instr)
        if new_block:
            chained = _try_chain(new_block[-1], instr)
            if chained is not None:
                new_block[-1] = chained
                continue
        new_block.append(instr)
    return new_block


def _try_chain(first, second):
    if not isinstance(first, instructions.Assignment):
        return None
    if not isinstance(second, instructions.Assignment):
        return None
    if not isinstance(first.dst.data_type, data_types.ClassType):
        return None
    if not isinstance(second.dst.data_type, data_types.ClassType):
        return None
    if second.src.emit_code() != first.dst.emit_code():
        return None
    if not _is_simple_lvalue(first.dst):
        return None
    return instructions.Assignment(
        second.dst, expressions.AssignmentExpression(first.dst, first.src))


def _is_simple_lvalue(e):
    """Variable or field of variable: reading it has no side effects."""
    while isinstance(e, expressions.FieldAccess):
        e = e.expression
    if isinstance(e, expressions.Dereference):
        e = e.expression
    return isinstance(e, expressions.Identifier)


def _chain_nested(instr):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _chain_block(else_block)
        return instructions.IfInstruction(
            instr.if_clause, _chain_block(instr.if_block), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _chain_block(instr.block))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _chain_block(instr.instructions))
    return instr
