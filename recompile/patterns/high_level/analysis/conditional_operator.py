import data_types
import expressions.intermediate
from expression_transformer import ExpressionTransformer
import instructions


class ConditionalOperatorAnalysis:
    def __init__(self):
        self._num_uses = {}
        self._candidates = []
        self._offsets = set()

    def on_transformation_finished(self):
        for offset in self._candidates:
            if self._num_uses[offset] == 3:
                self._offsets.add(offset)
        self._num_uses.clear()
        self._candidates.clear()

    def process_stackvar(self, offset, size):
        if offset not in self._num_uses:
            self._num_uses[offset] = 1
        elif self._num_uses[offset] is not None:
            self._num_uses[offset] += 1
        # Results of conditional operators are 32-bit values or doubles
        if size not in (4, 8):
            self._num_uses[offset] = None

    def process_local(self, local):
        self._num_uses[local.offset] = None

    def transform_block_instructions(
        self, block_instructions, stack_vars, characteristics=None, **kwargs
    ):
        if_instr = block_instructions.get_current_instruction(
            instructions.IfInstruction)
        if if_instr is None:
            return
        if_block = if_instr.if_block
        else_block = if_instr.else_block
        if else_block is None:
            return
        if len(if_block) != 1:
            return
        if_ass = if_block[0]
        if len(else_block) != 1:
            return
        else_ass = else_block[0]
        if not isinstance(if_ass, instructions.Assignment):
            return
        if not isinstance(else_ass, instructions.Assignment):
            return
        if_stackvar = if_ass.dst
        if not isinstance(if_stackvar, expressions.intermediate.Stackvar):
            return
        if if_stackvar.size not in (4, 8):
            return
        else_stackvar = else_ass.dst
        if not isinstance(else_stackvar, expressions.intermediate.Stackvar):
            return
        if else_stackvar.size != if_stackvar.size:
            return
        if if_stackvar.offset != else_stackvar.offset:
            return
        # Named variables are not results of conditional operators
        if (
            characteristics is not None and
            characteristics.variables_names.get(if_stackvar.offset)
            is not None
        ):
            return
        cond_operator_chain = block_instructions.interval(1)
        assert cond_operator_chain.as_instr(0, None) == if_instr
        next_instr = cond_operator_chain.as_instr(1, None)
        cond_operator = expressions.ConditionalOperator(
            if_instr.if_clause, if_ass.src, else_ass.src)
        next_instr = _replace_cond_operator(
            next_instr, if_stackvar, cond_operator)
        if next_instr is None:
            return
        self._candidates.append(if_stackvar.offset)
        if if_stackvar.offset not in self._offsets:
            return
        _add_stack_var(if_stackvar.offset, if_stackvar.size, stack_vars)
        cond_operator_chain.replace_instructions([next_instr])


class _CondOperandReplacer(ExpressionTransformer):
    def __init__(self, stackvar, cond_operator):
        self._stackvar = stackvar
        self._cond_operator = cond_operator
        self._num_replaced_expressions = 0

    @property
    def num_replaced_expressions(self):
        return self._num_replaced_expressions

    def transform_stackvar(self, offset, size):
        if self._stackvar.offset != offset:
            return None
        if self._stackvar.size != size:
            return None
        self._num_replaced_expressions += 1
        return self._cond_operator


def _replace_cond_operator(instr, stackvar, cond_operator):
    replacer = _CondOperandReplacer(stackvar, cond_operator)
    if isinstance(
        instr, (
            instructions.Assignment,
            instructions.CodeInstruction,
            instructions.ReturnInstruction,
            instructions.TemporaryRegisterDefinition)
    ):
        instr = instr.transform(replacer)
    elif isinstance(instr, instructions.IfInstruction):
        if_clause = instr.if_clause.transform(replacer)
        instr = instructions.IfInstruction(
            if_clause, instr.if_block, instr.else_block)
    else:
        return None
    if replacer.num_replaced_expressions != 1:
        return None
    return instr


def _add_stack_var(offset, size, stack_vars):
    if offset in stack_vars:
        return
    assert offset < 0
    name = "__cond_result_{:02X}".format(-offset)
    data_type = data_types.unknown_types[size]
    stack_vars[offset] = expressions.Identifier(data_type, name)
