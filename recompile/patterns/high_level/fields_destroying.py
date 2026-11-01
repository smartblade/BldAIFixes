import data_types
import expressions
import instructions
from instructions.extract_vtbl_addr_from_assign import\
    extract_vtbl_addr_from_assign

from .get_fields import get_fields


def discover_fields_destroying(procedure):
    if procedure.proc_decl is None:
        return procedure
    if not procedure.proc_decl.is_destructor:
        return procedure
    proc_info = procedure.proc_info
    class_type = procedure.proc_decl.method_class
    instrs = list(procedure.instructions)
    if class_type.has_virtual_methods:
        first_instr = instrs[0]
        if extract_vtbl_addr_from_assign(proc_info, first_instr) is not None:
            instrs = instrs[1:]
    fields = get_fields(class_type)
    for field in fields:
        field_type, field_name = field
        if not isinstance(field_type, data_types.ClassType):
            continue
        if not instrs:
            break
        last_instr = instrs[-1]
        if not is_destructor(proc_info, last_instr, field_type, field_name):
            break
        instrs.pop()
    return procedure.copy(instrs=instrs)


def is_destructor(proc_info, instr, class_type, field_name):
    if not isinstance(instr, instructions.CodeInstruction):
        return False
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return False
    if pc.proc_decl is None:
        return False
    if not pc.proc_decl.is_destructor:
        return False
    if pc.name != "~{}".format(class_type.class_name):
        return False
    if pc.name != pc.proc_decl.proc_name:
        return False
    if pc.proc_decl.method_class != class_type:
        return False
    if len(pc.arguments) != 1:
        return False
    obj_ptr = pc.arguments[0]
    if not isinstance(obj_ptr.data_type, data_types.Pointer32):
        return False
    obj_type = obj_ptr.data_type.pointee
    if proc_info.is_this_expression(obj_ptr):
        assert field_name is None
        return obj_type.parent == class_type
    if obj_type != class_type:
        return False
    if not isinstance(obj_ptr, expressions.AddressOf):
        return False
    obj = obj_ptr.expression
    if not isinstance(obj, expressions.FieldAccess):
        return False
    if not proc_info.is_this_expression(obj.expression):
        return False
    if obj.field_name != field_name:
        return False
    return True
