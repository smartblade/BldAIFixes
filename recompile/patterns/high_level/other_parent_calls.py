import data_types
import expressions
from expressions.operator import Operator
import instructions
from block_visitor import visit_block


def restore_other_parent_calls(instrs, analysis=None):
    """Restore calls of methods of other parents of objects created by new.

    A method of other parent of multiple inheritance is called with the
    address of the parent in the object, computed into a temporary:
        t = (int)p + 4;
        Append(t, x);
    If p is assigned by 'new T(...)' and T has other parent at the offset,
    the call is restored as a call of the method by p: 'p->Append(x)'.
    The type of p is passed to the analysis: the integer addition made it
    unknown before.
    """
    created_types = _created_types(instrs)
    if not created_types:
        return instrs
    uses = _count_stackvar_uses(instrs)
    restored = set()
    new_instrs = _restore_block(instrs, created_types, uses, restored)
    if analysis is not None:
        for offset in restored:
            analysis.set_stackvar_type(
                offset, data_types.Pointer32(created_types[offset]))
    return new_instrs


def _restore_block(block, created_types, uses, restored):
    new_block = []
    i = 0
    while i < len(block):
        instr = _restore_nested(block[i], created_types, uses, restored)
        if i + 1 < len(block):
            call = _restore_pair(
                instr, block[i + 1], created_types, uses, restored)
            if call is not None:
                new_block.append(call)
                i += 2
                continue
        new_block.append(instr)
        i += 1
    return new_block


def _restore_nested(instr, created_types, uses, restored):
    def restore(block):
        return _restore_block(block, created_types, uses, restored)

    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = restore(else_block)
        return instructions.IfInstruction(
            instr.if_clause, restore(instr.if_block), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, restore(instr.block))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, restore(instr.instructions))
    return instr


def _restore_pair(assignment, call, created_types, uses, restored):
    if not isinstance(assignment, instructions.Assignment):
        return None
    temporary = assignment.dst
    if not isinstance(temporary, expressions.intermediate.Stackvar):
        return None
    # The temporary is assigned and passed to the method only
    if uses.get(temporary.offset, 0) != 2:
        return None
    adjusted = _adjusted_pointer(assignment.src)
    if adjusted is None:
        return None
    obj, offset = adjusted
    class_type = created_types.get(obj.offset)
    if class_type is None:
        return None
    parent = dict(class_type.other_parents).get(offset)
    if parent is None:
        return None
    if not isinstance(call, instructions.CodeInstruction):
        return None
    pc = call.expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return None
    if not pc.arguments or not _is_stackvar(
        _strip_cast(pc.arguments[0]), temporary
    ):
        return None
    this = expressions.ImplicitCast(data_types.Pointer32(parent), obj)
    restored.add(obj.offset)
    return instructions.CodeInstruction(
        pc.copy(arguments=[this] + list(pc.arguments[1:])))


def _adjusted_pointer(e):
    """Return (pointer, offset) of '(int)p + offset'."""
    if not isinstance(e, expressions.Bin) or e.operator != Operator.ADD:
        return None
    obj = _strip_cast(e.left)
    if not isinstance(obj, expressions.intermediate.Stackvar):
        return None
    if obj.size != 4:
        return None
    if not isinstance(e.right, expressions.Constant):
        return None
    if not isinstance(e.right.value, int) or e.right.value <= 0:
        return None
    return obj, e.right.value


def _created_types(instrs):
    """Classes of objects created by new by offsets of stack variables."""
    created = {}
    assigned = {}
    for instr in _assignments(instrs):
        dst = instr.dst
        if not isinstance(dst, expressions.intermediate.Stackvar):
            continue
        assigned[dst.offset] = assigned.get(dst.offset, 0) + 1
        if isinstance(instr.src, expressions.NewExpression):
            created[dst.offset] = instr.src.class_type
    # Variables assigned once by new only
    return dict(
        (offset, class_type) for offset, class_type in created.items()
        if assigned[offset] == 1
    )


def _assignments(block):
    for instr in block:
        if isinstance(instr, instructions.Assignment):
            yield instr
        for attr in ("if_block", "else_block", "block", "instructions"):
            sub = getattr(instr, attr, None)
            if isinstance(sub, list):
                yield from _assignments(sub)


def _strip_cast(e):
    while isinstance(e, expressions.ReinterpretCast):
        e = e.expression
    return e


def _is_stackvar(e, stackvar):
    return (
        isinstance(e, expressions.intermediate.Stackvar) and
        e.offset == stackvar.offset and e.size == stackvar.size
    )


def _count_stackvar_uses(instrs):
    uses = {}

    def on_visit(e, **kwargs):
        if isinstance(e, expressions.intermediate.Stackvar):
            uses[e.offset] = uses.get(e.offset, 0) + 1

    visit_block(instrs, on_visit)
    return uses
