import data_types
import expressions
import instructions
from block_visitor import visit_block


def fold_new_expressions(instrs, analysis=None):
    """Fold creation of objects by operator new into 'new T(args)'.

    Visual C++ compiles 'p = new T(a);' into a call of operator new and a
    conditional call of the constructor of the allocated memory:
        t = operator new(sizeof(T));
        p = t != 0 ? T(t, a) : 0;
    The temporary t isn't used anywhere else. The type of the variable
    assigned by the new expression is passed to the analysis: the variable
    may be typed as a pointer to a parent before, e.g. by a return.
    """
    uses = _count_stackvar_uses(instrs)
    new_instrs = _fold_block(instrs, uses)
    if analysis is not None:
        for instr in _assignments(new_instrs):
            if isinstance(instr.src, expressions.NewExpression):
                analysis.process_assignment(instr.dst, instr.src)
    return new_instrs


def _assignments(block):
    for instr in block:
        if isinstance(instr, instructions.Assignment):
            yield instr
        for attr in ("if_block", "else_block", "block", "instructions"):
            sub = getattr(instr, attr, None)
            if isinstance(sub, list):
                yield from _assignments(sub)


def _fold_block(block, uses):
    new_block = []
    i = 0
    while i < len(block):
        instr = _fold_nested(block[i], uses)
        if i + 1 < len(block):
            new_instr = _fold_pair(instr, block[i + 1], uses)
            if new_instr is not None:
                new_block.append(new_instr)
                i += 2
                continue
        new_block.append(instr)
        i += 1
    return new_block


def _fold_nested(instr, uses):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _fold_block(else_block, uses)
        return instructions.IfInstruction(
            instr.if_clause, _fold_block(instr.if_block, uses), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _fold_block(instr.block, uses))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _fold_block(instr.instructions, uses))
    return instr


def _fold_pair(allocation, construction, uses):
    temporary = _allocated_temporary(allocation)
    if temporary is None:
        return None
    # The temporary is assigned, compared with 0 and passed to constructor
    if uses.get(temporary.offset, 0) != 3:
        return None
    if not isinstance(construction, instructions.Assignment):
        return None
    conditional = construction.src
    if not isinstance(conditional, expressions.ConditionalOperator):
        return None
    if not _is_not_null_check(conditional.if_clause, temporary):
        return None
    if not _is_null(conditional.else_expression):
        return None
    pc = conditional.then_expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return None
    if pc.proc_decl is None or not pc.proc_decl.is_constructor:
        return None
    if not pc.arguments or not _is_stackvar(
        _strip_cast(pc.arguments[0]), temporary
    ):
        return None
    class_type = pc.proc_decl.method_class
    if not isinstance(class_type, data_types.ClassType):
        return None
    new_expression = expressions.NewExpression(class_type, pc.arguments[1:])
    return instructions.Assignment(construction.dst, new_expression)


def _allocated_temporary(instr):
    if not isinstance(instr, instructions.Assignment):
        return None
    dst = instr.dst
    if not isinstance(dst, expressions.intermediate.Stackvar):
        return None
    pc = _strip_cast(instr.src)
    if not isinstance(pc, expressions.ProcedureCall):
        return None
    if pc.name != "operator new" or len(pc.arguments) != 1:
        return None
    if not isinstance(pc.arguments[0], expressions.Constant):
        return None
    return dst


def _is_not_null_check(e, temporary):
    if not isinstance(e, expressions.Bin):
        return False
    if e.operator.value != "!=":
        return False
    return _is_stackvar(_strip_cast(e.left), temporary) and _is_null(e.right)


def _is_null(e):
    if e is expressions.Null:
        return True
    return isinstance(e, expressions.Constant) and e.value == 0


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
