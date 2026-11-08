import expressions
from expression_transformer import ExpressionTransformer
import instructions

_unnamed_prefix = "unknown_loc_"


def fold_conditional_results(procedure):
    """Fold results of conditional operators kept in typed temporaries.

        if (c) { t = a; } else { t = b; } x = t;  ->  x = c ? a : b;

    Temporaries of 32-bit values are folded by the analysis of conditional
    operators before stack variables are typed, temporaries typed before,
    e.g. doubles of macros min and max, are folded here if they are unnamed
    and used by the conditional operator and the next instruction only.
    """
    uses = _count_uses(procedure.instructions)
    instrs = _fold_block(list(procedure.instructions), uses)
    return procedure.copy(instrs=instrs)


def _fold_block(block, uses):
    block = [_fold_nested(instr, uses) for instr in block]
    new_block = []
    i = 0
    while i < len(block):
        if i + 1 < len(block):
            folded = _try_fold(block[i], block[i + 1], uses)
            if folded is not None:
                new_block.append(folded)
                i += 2
                continue
        new_block.append(block[i])
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
    block = getattr(instr, "block", None)
    if isinstance(block, list) and hasattr(instr, "copy"):
        return instr.copy(block=_fold_block(block, uses))
    return instr


def _try_fold(if_instr, use, uses):
    if not isinstance(if_instr, instructions.IfInstruction):
        return None
    if if_instr.else_block is None:
        return None
    if len(if_instr.if_block) != 1 or len(if_instr.else_block) != 1:
        return None
    then_ass, else_ass = if_instr.if_block[0], if_instr.else_block[0]
    for ass in (then_ass, else_ass):
        if not isinstance(ass, instructions.Assignment):
            return None
    var = then_ass.dst
    if not isinstance(var, expressions.Identifier):
        return None
    if not var.name.startswith(_unnamed_prefix):
        return None
    if not _is_variable(else_ass.dst, var):
        return None
    if uses.get(var.name) != 3:
        return None
    conditional = expressions.ConditionalOperator(
        if_instr.if_clause, then_ass.src, else_ass.src)
    if not isinstance(use, (
        instructions.Assignment, instructions.CodeInstruction,
        instructions.ReturnInstruction,
    )):
        return None
    replacer = _Replacer(var, conditional)
    new_use = use.transform(replacer)
    if replacer.num_replaced != 1:
        return None
    return new_use


class _Replacer(ExpressionTransformer):
    def __init__(self, var, expression):
        self._var = var
        self._expression = expression
        self.num_replaced = 0

    def transform_identifier(self, identifier, **kwargs):
        if not _is_variable(identifier, self._var):
            return None
        self.num_replaced += 1
        return self._expression


def _is_variable(e, var):
    return isinstance(e, expressions.Identifier) and e.name == var.name


def _count_uses(instrs):
    uses = {}

    def on_visit(e, **kwargs):
        if isinstance(e, expressions.Identifier):
            uses[e.name] = uses.get(e.name, 0) + 1

    for instr in instrs:
        instr.visit(on_visit)
    return uses
