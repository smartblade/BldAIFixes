import data_types
import expressions
import instructions
from instructions.extract_vtbl_addr_from_assign import\
    extract_vtbl_addr_from_assign

from .get_fields import get_fields


def remove_inlined_member_construction(procedure):
    """Remove inlined default constructors of fields in constructors.

    Visual C++ inlines the inline default constructor of a field of a class
    type, it assigns all fields of the field in the order of declaration:
        this->center.x = 0.0; this->center.y = 0.0; this->center.z = 0.0;
    A field not at the start of the object is constructed by a pointer to it
    in a temporary variable, the 'this' of the inlined constructor:
        p = &this->center; p->x = 0.0; p->y = 0.0; p->z = 0.0;
    The construction of the field is implicit in C++. Values assigned by the
    default constructor aren't checked.
    """
    proc_decl = procedure.proc_decl
    if proc_decl is None or not proc_decl.is_constructor:
        return procedure
    proc_info = procedure.proc_info
    instrs = list(procedure.instructions)
    i = 0
    while i < len(instrs):
        count = _member_construction_length(proc_info, instrs, i)
        if count:
            del instrs[i:i + count]
            continue
        if not _is_initialization(proc_info, instrs[i]):
            break
        i += 1
    return procedure.copy(instrs=instrs)


def _member_construction_length(proc_info, instrs, index):
    pointer_member = _member_pointer_assignment(proc_info, instrs[index])
    if pointer_member is not None:
        return _member_construction_by_pointer_length(
            instrs, index, *pointer_member)
    member = _assigned_member(proc_info, instrs[index])
    if member is None:
        return 0
    member_name, member_type = member
    if not has_default_constructor(member_type):
        return 0
    member_fields = get_fields(member_type)
    if not member_fields or len(instrs) - index < len(member_fields):
        return 0
    for k, (field_type, field_name) in enumerate(member_fields):
        instr = instrs[index + k]
        if (
            isinstance(field_type, data_types.ClassType) or
            _assigned_member(proc_info, instr) != member or
            instr.dst.field_name != field_name or
            not isinstance(instr.src, expressions.Constant)
        ):
            return 0
    return len(member_fields)


def _member_construction_by_pointer_length(
    instrs, index, pointer, member_type
):
    """Length of 'p = &this->f; p->x = c; ...' constructing all fields of f."""
    if not has_default_constructor(member_type):
        return 0
    member_fields = get_fields(member_type)
    if not member_fields or len(instrs) - index - 1 < len(member_fields):
        return 0
    for k, (field_type, field_name) in enumerate(member_fields):
        instr = instrs[index + 1 + k]
        if (
            isinstance(field_type, data_types.ClassType) or
            not isinstance(instr, instructions.Assignment) or
            not isinstance(instr.dst, expressions.FieldAccess) or
            not _is_identifier(instr.dst.expression, pointer) or
            instr.dst.field_name != field_name or
            not isinstance(instr.src, expressions.Constant)
        ):
            return 0
    count = 1 + len(member_fields)
    # The pointer is the 'this' of the inlined constructor only: it is
    # assigned again before other uses
    for instr in instrs[index + count:]:
        if (
            isinstance(instr, instructions.Assignment) and
            _is_identifier(instr.dst, pointer)
        ):
            break
        if _uses_identifier(instr, pointer):
            return 0
    return count


def _member_pointer_assignment(proc_info, instr):
    """Return (pointer, type of field) of 'p = &this->f' to local p."""
    if not isinstance(instr, instructions.Assignment):
        return None
    if not isinstance(instr.dst, expressions.Identifier):
        return None
    if proc_info.is_this_expression(instr.dst):
        return None
    src = instr.src
    if not isinstance(src, expressions.AddressOf):
        return None
    member = src.expression
    if not isinstance(member, expressions.FieldAccess):
        return None
    if not proc_info.is_this_expression(member.expression):
        return None
    member_type = member.data_type
    if not isinstance(member_type, data_types.ClassType):
        return None
    return instr.dst, member_type


def _is_identifier(e, identifier):
    return (
        isinstance(e, expressions.Identifier) and e.name == identifier.name
    )


def _uses_identifier(instr, identifier):
    used = []

    def on_visit(e, **kwargs):
        if _is_identifier(e, identifier):
            used.append(e)

    instr.visit(on_visit)
    return bool(used)


def _assigned_member(proc_info, instr):
    """Return (name, type) of field of this assigned by 'this->f.x = e'."""
    if not isinstance(instr, instructions.Assignment):
        return None
    dst = instr.dst
    if not isinstance(dst, expressions.FieldAccess):
        return None
    member_ptr = dst.expression
    if not isinstance(member_ptr, expressions.AddressOf):
        return None
    member = member_ptr.expression
    if not isinstance(member, expressions.FieldAccess):
        return None
    if not proc_info.is_this_expression(member.expression):
        return None
    member_type = member.data_type
    if not isinstance(member_type, data_types.ClassType):
        return None
    return member.field_name, member_type


def has_default_constructor(class_type):
    return any(
        len(constructor.get_parameters_ids()) == 1
        for constructor in class_type.constructors
    )


def _is_initialization(proc_info, instr):
    """Check for code of initialization of fields and parents."""
    if extract_vtbl_addr_from_assign(proc_info, instr) is not None:
        return True
    if isinstance(instr, instructions.Assignment):
        dst = instr.dst
        return (
            isinstance(dst, expressions.FieldAccess) and
            proc_info.is_this_expression(dst.expression)
        )
    if isinstance(instr, instructions.CodeInstruction):
        pc = instr.expression
        return (
            isinstance(pc, expressions.ProcedureCall) and
            pc.proc_decl is not None and pc.proc_decl.is_constructor
        )
    return False
