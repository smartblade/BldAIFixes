import expressions
import instructions
from instructions.extract_vtbl_addr_from_assign import\
    extract_vtbl_addr_from_assign


def remove_inlined_base_structors(procedure):
    """Remove code of constructors and destructors of base classes.

    Visual C++ inlines constructors and destructors of base classes with
    assignments of their virtual methods tables. Base constructors are
    called implicitly before the code of the constructor and base
    destructors are called implicitly after the code of the destructor.
    """
    proc_decl = procedure.proc_decl
    if proc_decl is None or proc_decl.method_class is None:
        return procedure
    class_type = proc_decl.method_class
    if class_type.parent is None or not class_type.has_virtual_methods:
        return procedure
    proc_info = procedure.proc_info
    instrs = list(procedure.instructions)
    vtbl_indices = [
        i for i, instr in enumerate(instrs)
        if extract_vtbl_addr_from_assign(proc_info, instr) is not None
    ]
    if not vtbl_indices or vtbl_indices[0] != 0:
        return procedure
    if proc_decl.is_constructor:
        if len(vtbl_indices) < 2:
            return procedure
        end = _find_own_initialization(
            proc_info, class_type, instrs, vtbl_indices[-1])
        own_vtbl_index = vtbl_indices[-1]
        removed = instrs[:end] + [instrs[own_vtbl_index]]
        # Assignment of the table of the class is implicit too
        instrs = instrs[end:own_vtbl_index] + instrs[own_vtbl_index + 1:]
        if any(_has_label(instr) for instr in removed):
            return procedure
    elif proc_decl.is_destructor:
        start = _find_base_destruction(proc_info, class_type, instrs)
        if start is None:
            return procedure
        instrs = instrs[:start]
    else:
        return procedure
    instrs = [
        instr for instr in instrs
        if not _is_secondary_vtbl_assign(proc_info, class_type, instr)
    ]
    return procedure.copy(instrs=instrs)


def _find_base_destruction(proc_info, class_type, instrs):
    """Find start of inlined destructors of base classes.

    Destructors of base classes start with assignments of their tables.
    Their code may have labels if it isn't jumped to from the code of the
    destructor.
    """
    for start in range(1, len(instrs)):
        instr = instrs[start]
        if (
            extract_vtbl_addr_from_assign(proc_info, instr) is not None or
            _is_secondary_vtbl_assign(proc_info, class_type, instr)
        ):
            break
    else:
        return None
    removed = instrs[start:]
    if not any(_has_vtbl_assign(proc_info, instr) for instr in removed):
        return None
    removed_labels = _collect(removed, instructions.LabeledBlock)
    removed_labels = set(block.label for block in removed_labels)
    gotos = _collect(instrs[:start], instructions.Goto)
    if any(goto.label in removed_labels for goto in gotos):
        return None
    return start


def _has_vtbl_assign(proc_info, instr):
    return any(
        extract_vtbl_addr_from_assign(proc_info, assignment) is not None
        for assignment in _collect([instr], instructions.Assignment)
    )


def _collect(instrs, instr_type):
    found = []

    def on_visit(e, **kwargs):
        if isinstance(e, instr_type):
            found.append(e)

    for instr in instrs:
        instr.visit(on_visit)
    return found


def _find_own_initialization(proc_info, class_type, instrs, own_vtbl_index):
    """Find the first instruction initializing fields of the class."""
    own_fields = set(
        field_name for field_type, field_name in class_type.fields.values())
    for i, instr in enumerate(instrs[:own_vtbl_index]):
        if not isinstance(instr, instructions.Assignment):
            continue
        dst = instr.dst
        if (
            isinstance(dst, expressions.FieldAccess) and
            proc_info.is_this_expression(dst.expression) and
            dst.field_name in own_fields
        ):
            return i
    return own_vtbl_index


def _is_secondary_vtbl_assign(proc_info, class_type, instr):
    """Check if instruction assigns table of other parent of the class."""
    if not isinstance(instr, instructions.Assignment):
        return False
    dst = instr.dst
    if not isinstance(dst, expressions.intermediate.Access):
        return False
    if dst.size != 4 or dst.offset == 0:
        return False
    if not proc_info.is_this_expression(dst.expression):
        return False
    # Tables of fields are assigned by inlined methods of the fields
    if class_type.find_nearest_field_offset(dst.offset) is not None:
        return False
    return isinstance(instr.src, expressions.intermediate.Global)


def _has_label(instr):
    return bool(_collect([instr], instructions.LabeledBlock))
