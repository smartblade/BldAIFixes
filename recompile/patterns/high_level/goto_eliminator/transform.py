import expressions
import instructions

from .eliminate_unused_label import eliminate_unused_label
from .find_return_label import find_return_label
from .collect_label_uses import collect_label_uses
from .transform_if import transform_if_statements
from .transform_switch import transform_switch_statements
from .transform_while import transform_while


def transform(instrs, stack_vars):
    return_label = find_return_label(instrs)
    label_uses = collect_label_uses(instrs)
    new_instructions = []
    for instr in instrs:
        instr = _transform_instruction(
            instr, return_label=return_label, label_uses=label_uses,
            stack_vars=stack_vars)
        new_instructions.append(instr)
    eliminate_unused_label(new_instructions, label_uses=label_uses)
    new_instructions = transform_switch_statements(
        new_instructions, label_uses=label_uses, stack_vars=stack_vars)
    new_instructions = transform_if_statements(
        new_instructions, label_uses=label_uses, stack_vars=stack_vars)
    return new_instructions


def _transform_instruction(instr, return_label, label_uses, stack_vars):
    if isinstance(instr, instructions.Goto):
        if instr.label == return_label:
            label_uses[return_label].remove(instr)
            return instructions.ReturnInstruction(None)
    if isinstance(instr, instructions.LabeledBlock):
        return _transform_labeled_block(
            instr, return_label=return_label, label_uses=label_uses,
            stack_vars=stack_vars)
    return instr


def _transform_labeled_block(labeled_block, **kwargs):
    new_instructions = []
    for instr in labeled_block.instructions:
        new_instructions.append(_transform_instruction(instr, **kwargs))
    eliminate_unused_label(new_instructions, **kwargs)
    new_instructions = transform_switch_statements(new_instructions, **kwargs)
    new_instructions = transform_if_statements(new_instructions, **kwargs)
    transform_while(labeled_block.label, new_instructions, **kwargs)
    return instructions.LabeledBlock(labeled_block.label, new_instructions)



def transform_forward_gotos(instrs, stack_vars):
    """Eliminate forward gotos over loops restored after the elimination.

    Labels may be nested in labeled blocks of loops at the first
    elimination, they are in the same block when loops are restored:
        if (c) goto l; ...; for (...) {...} return x; l: ...
    The code jumped over ends with return, the labeled code is the else
    block: its variables are in a block of the stack frame like in
        if (!c) { ...; return x; } else { ... }
    """
    label_uses = collect_label_uses(instrs)
    return _transform_forward_gotos_block(list(instrs), label_uses)


def _transform_forward_gotos_block(instrs, label_uses):
    if not instrs:
        return instrs
    labeled_block = instrs[-1]
    if not isinstance(labeled_block, instructions.LabeledBlock):
        return instrs
    if len(label_uses.get(labeled_block.label, ())) != 1:
        return instrs
    for i, instr in enumerate(instrs[:-1]):
        if not isinstance(instr, instructions.IfInstruction):
            continue
        if instr.else_block is not None or len(instr.if_block) != 1:
            continue
        goto = instr.if_block[0]
        if not isinstance(goto, instructions.Goto):
            continue
        if goto.label != labeled_block.label:
            continue
        jumped = instrs[i + 1:-1]
        if not jumped or not isinstance(
            jumped[-1], instructions.ReturnInstruction
        ):
            return instrs
        label_uses[goto.label].remove(goto)
        else_block = _transform_forward_gotos_block(
            labeled_block.instructions, label_uses)
        return instrs[:i] + [instructions.IfInstruction(
            expressions.do_logical_not(instr.if_clause), jumped,
            else_block)]
    return instrs
