import data_types
import expressions
import instructions


def remove_member_array_construction(procedure):
    """Remove construction of elements of array fields in constructors.

    Visual C++ constructs elements of array fields with a loop calling
    the default constructor of elements:
        count = N;
        size = sizeof(T);
        ptr = &this->field;
        while (--count >= 0) { ptr->T(); ptr += size; }
    The construction is implicit in C++.
    """
    proc_decl = procedure.proc_decl
    if proc_decl is None or not proc_decl.is_constructor:
        return procedure
    proc_info = procedure.proc_info
    instrs = list(procedure.instructions)
    i = 3
    while i < len(instrs):
        if _is_array_construction(proc_info, instrs[i - 3:i + 1]):
            del instrs[i - 3:i + 1]
        else:
            i += 1
    return procedure.copy(instrs=instrs)


def _is_array_construction(proc_info, instrs):
    count_instr, size_instr, ptr_instr, loop = instrs
    if not isinstance(loop, instructions.WhileInstruction):
        return False
    if len(loop.block) != 2:
        return False
    if not all(
        isinstance(instr, instructions.Assignment)
        for instr in (count_instr, size_instr, ptr_instr)
    ):
        return False
    ptr = ptr_instr.dst
    if not isinstance(ptr, expressions.intermediate.Stackvar):
        return False
    field_ptr = ptr_instr.src
    if not isinstance(field_ptr, expressions.AddressOf):
        return False
    field = field_ptr.expression
    if not isinstance(field, expressions.FieldAccess):
        return False
    if not proc_info.is_this_expression(field.expression):
        return False
    array_type = field.data_type
    if not isinstance(array_type, data_types.Array):
        return False
    element_type = array_type.element_type
    if not isinstance(element_type, data_types.ClassType):
        return False
    if not _is_constant(count_instr.src, array_type.length):
        return False
    if not _is_constant(size_instr.src, element_type.size):
        return False
    call, increment = loop.block
    if not _is_default_constructor_call(call, ptr, element_type):
        return False
    if not isinstance(increment, instructions.Assignment):
        return False
    return _is_stackvar(increment.dst, ptr)


def _is_default_constructor_call(instr, ptr, class_type):
    if not isinstance(instr, instructions.CodeInstruction):
        return False
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return False
    if pc.proc_decl is None or not pc.proc_decl.is_constructor:
        return False
    if pc.proc_decl.method_class.class_name != class_type.class_name:
        return False
    if len(pc.arguments) != 1:
        return False
    obj = pc.arguments[0]
    while isinstance(
        obj, (expressions.ReinterpretCast, expressions.ImplicitCast)
    ):
        obj = obj.expression
    return _is_stackvar(obj, ptr)


def _is_stackvar(e, stackvar):
    return (
        isinstance(e, expressions.intermediate.Stackvar) and
        e.offset == stackvar.offset
    )


def _is_constant(e, value):
    return isinstance(e, expressions.Constant) and e.value == value
