import data_types
import expressions
import instructions

from .transform_class_returns import _find_constructor


def restore_local_constructions(procedure):
    """Restore constructions of local objects by inlined constructors.

    'B_Vector v; v.x = a; v.y = b; v.z = c;' is restored as
    'B_Vector v(a, b, c);' if the class has a constructor with parameters
    of types of its fields. A call of a constructor that is not inlined
    right after the declaration, 'B_BoundingBox b; b.B_BoundingBox(x, y);',
    is restored as 'B_BoundingBox b(x, y);'.
    """
    instrs = _restore_block(list(procedure.instructions))
    return procedure.copy(instrs=instrs)


def _restore_block(block):
    new_block = []
    i = 0
    while i < len(block):
        instr = _restore_nested(block[i])
        construction = _make_construction(instr, block[i + 1:])
        if construction is not None:
            declaration, num_assignments = construction
            new_block.append(declaration)
            i += 1 + num_assignments
            continue
        construction = _make_called_construction(instr, block[i + 1:])
        if construction is not None:
            new_instrs, num_instrs = construction
            new_block.extend(new_instrs)
            i += 1 + num_instrs
            continue
        new_block.append(instr)
        i += 1
    return new_block


def _make_construction(instr, next_instrs):
    if not isinstance(instr, instructions.VariableDeclaration):
        return None
    if instr.initial_expression is not None:
        return None
    var = instr.identifier
    class_type = var.data_type
    if not isinstance(class_type, data_types.ClassType):
        return None
    fields = [field for offset, field in sorted(class_type.fields.items())]
    if not fields or len(next_instrs) < len(fields):
        return None
    if class_type.parent is not None or class_type.has_virtual_methods:
        return None
    if _find_constructor(class_type, fields) is None:
        return None
    values = []
    for assignment, (field_type, field_name) in zip(next_instrs, fields):
        if not isinstance(assignment, instructions.Assignment):
            return None
        dst = assignment.dst
        if not isinstance(dst, expressions.FieldAccess):
            return None
        if dst.field_name != field_name or not _is_variable(
            dst.expression, var
        ):
            return None
        if _uses_variable(assignment.src, var):
            return None
        values.append(assignment.src)
    construction = expressions.ProcedureCall(
        name=class_type.class_name, is_method=False, arguments=values)
    declaration = instructions.VariableDeclaration(
        var, construction, is_direct_initialization=True)
    return declaration, len(fields)


def _make_called_construction(instr, next_instrs):
    """Restore 'T v; v.T(args);' as 'T v(args);', 'T v; v.T();' as 'T v;'.

    Declarations of temporaries of the arguments may be between the
    declaration and the call, they are kept before the construction.
    Return (instructions, number of replaced next instructions).
    """
    if not isinstance(instr, instructions.VariableDeclaration):
        return None
    if instr.initial_expression is not None:
        return None
    var = instr.identifier
    if not isinstance(var.data_type, data_types.ClassType):
        return None
    k = 0
    while (
        k < len(next_instrs) and
        isinstance(next_instrs[k], instructions.VariableDeclaration) and
        next_instrs[k].initial_expression is None
    ):
        k += 1
    if k == len(next_instrs):
        return None
    call = next_instrs[k]
    if not isinstance(call, instructions.CodeInstruction):
        return None
    pc = call.expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return None
    if pc.proc_decl is None or not pc.proc_decl.is_constructor:
        return None
    if pc.proc_decl.method_class is not var.data_type:
        return None
    if not pc.arguments or not _is_variable(pc.arguments[0], var):
        return None
    arguments = pc.arguments[1:]
    if not arguments:
        # Called default constructor: 'T v; v.T();' is 'T v;'
        return list(next_instrs[:k]) + [instr], k + 1
    if any(_uses_variable(argument, var) for argument in arguments):
        return None
    construction = expressions.ProcedureCall(
        name=var.data_type.class_name, is_method=False, arguments=arguments)
    declaration = instructions.VariableDeclaration(
        var, construction, is_direct_initialization=True)
    return list(next_instrs[:k]) + [declaration], k + 1


def _is_variable(e, var):
    if isinstance(e, expressions.AddressOf):
        e = e.expression
    return e is var or (
        isinstance(e, expressions.Identifier) and e.name == var.name)


def _uses_variable(e, var):
    found = []

    def on_visit(sub_e, **kwargs):
        if _is_variable(sub_e, var):
            found.append(sub_e)

    e.visit(on_visit)
    return bool(found)


def _restore_nested(instr):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _restore_block(else_block)
        return instructions.IfInstruction(
            instr.if_clause, _restore_block(instr.if_block), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _restore_block(instr.block))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _restore_block(instr.instructions))
    if isinstance(instr, instructions.Switch):
        for label, block in instr.blocks_dict.items():
            instr.blocks_dict[label] = _restore_block(block)
        return instr
    # Loops with blocks of other kinds, e.g. 'for' loops
    block = getattr(instr, "block", None)
    if isinstance(block, list) and hasattr(instr, "copy"):
        return instr.copy(block=_restore_block(block))
    return instr
