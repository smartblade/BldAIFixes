import instructions


def split_jumped_declarations(procedure):
    """Split declarations with initialization bypassed by jumps.

    C++ does not allow to jump past a declaration with initialization into
    the scope of the variable, so 'T x = e;' is replaced with 'T x; x = e;'
    if there is a jump from outside of the scope of the variable to a label
    in its scope.
    """
    label_uses = _count_label_uses(procedure.instructions)
    instrs = _split_block(list(procedure.instructions), label_uses)
    return procedure.copy(instrs=instrs)


def _split_block(block, label_uses):
    new_block = []
    for index, instr in enumerate(block):
        instr = _split_nested(instr, label_uses)
        if (
            isinstance(instr, instructions.VariableDeclaration) and
            instr.initial_expression is not None and
            _is_jumped_into(block[index + 1:], label_uses)
        ):
            new_block.append(
                instructions.VariableDeclaration(instr.identifier, None))
            new_block.append(instructions.Assignment(
                instr.identifier, instr.initial_expression))
        else:
            new_block.append(instr)
    return new_block


def _is_jumped_into(scope, label_uses):
    """Check if a label in the scope is used by a jump out of the scope."""
    labels = []
    gotos = {}
    for instr in scope:
        instr.visit(_collect_labels_and_gotos, labels=labels, gotos=gotos)
    return any(
        gotos.get(label, 0) < label_uses.get(label, 0) for label in labels)


def _count_label_uses(block):
    gotos = {}
    for instr in block:
        instr.visit(_collect_labels_and_gotos, labels=[], gotos=gotos)
    return gotos


def _collect_labels_and_gotos(e, labels, gotos):
    if isinstance(e, instructions.LabeledBlock):
        labels.append(e.label)
    elif isinstance(e, instructions.Goto):
        gotos[e.label] = gotos.get(e.label, 0) + 1


def _split_nested(instr, label_uses):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _split_block(else_block, label_uses)
        return instructions.IfInstruction(
            instr.if_clause,
            _split_block(instr.if_block, label_uses),
            else_block,
        )
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _split_block(instr.block, label_uses))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _split_block(instr.instructions, label_uses))
    if isinstance(instr, instructions.Switch):
        for label, block in instr.blocks_dict.items():
            instr.blocks_dict[label] = _split_block(block, label_uses)
    return instr
