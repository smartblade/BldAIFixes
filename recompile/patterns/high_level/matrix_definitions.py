import instructions

# Macros defining all elements of a matrix field of a class:
# (class name, field name): (macro name, rows, columns)
_MATRIX_MACROS = {
    ("B_Matrix", "m"): ("DEFINE_MATRIX", 4, 4),
}


def collapse_matrix_definitions(procedure):
    """Replace assignments to all elements of a matrix field of 'this' in
    the order of rows with a macro defining the matrix.

    'this->m[0][0] = a; this->m[0][1] = b; ...' -> 'DEFINE_MATRIX(a, b, ...)'
    """
    proc_decl = procedure.proc_decl
    if proc_decl is None or proc_decl.method_class is None:
        return procedure
    class_name = proc_decl.method_class.class_name
    instrs = list(procedure.instructions)
    changed = False
    for (macro_class, field_name), macro in _MATRIX_MACROS.items():
        if macro_class != class_name:
            continue
        instrs, collapsed = _collapse_block(instrs, field_name, *macro)
        changed = changed or collapsed
    if not changed:
        return procedure
    return procedure.copy(instrs=instrs)


def _collapse_block(block, field_name, macro_name, num_rows, num_columns):
    num_elements = num_rows * num_columns
    expected_destinations = [
        "this->{}[{}][{}]".format(field_name, row, column)
        for row in range(num_rows)
        for column in range(num_columns)
    ]
    new_block = []
    collapsed = False
    index = 0
    while index < len(block):
        candidates = block[index:index + num_elements]
        if (
            len(candidates) == num_elements and
            all(
                isinstance(instr, instructions.Assignment) and
                instr.dst.emit_code() == destination
                for instr, destination in zip(
                    candidates, expected_destinations)
            )
        ):
            elements = [instr.src for instr in candidates]
            rows = [
                elements[row * num_columns:(row + 1) * num_columns]
                for row in range(num_rows)
            ]
            new_block.append(instructions.MatrixDefinition(macro_name, rows))
            collapsed = True
            index += num_elements
            continue
        new_block.append(block[index])
        index += 1
    return new_block, collapsed
