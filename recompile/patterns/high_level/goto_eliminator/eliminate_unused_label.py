import instructions


def eliminate_unused_label(instrs, label_uses, **kwargs):
    labeled_block = instrs[-1]
    if (
        isinstance(labeled_block, instructions.LabeledBlock) and
        not label_uses.get(labeled_block.label)
    ):
        instrs.pop()
        instrs.extend(labeled_block.instructions)
