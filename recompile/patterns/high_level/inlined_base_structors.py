from calling_convention import CallingConvention
import expressions
from expressions.operator import Operator
import instructions
from procedure_declaration import ProcedureDeclaration
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
        instrs = _make_other_parents_construction(
            proc_info, class_type, removed) + instrs
    elif proc_decl.is_destructor:
        start = _find_base_destruction(proc_info, class_type, instrs)
        if start is None:
            return procedure
        instrs = _replace_parent_pointers(
            proc_info, class_type, instrs[:start])
    else:
        return procedure
    instrs = [
        instr for instr in instrs
        if not _is_secondary_vtbl_assign(proc_info, class_type, instr)
    ]
    return procedure.copy(instrs=instrs)


def _make_other_parents_construction(proc_info, class_type, removed):
    """Make calls of constructors of other parents with not default values.

    Constructors of other parents of multiple inheritance are inlined with
    a pointer to the parent: 'p = this + 4; p->increment = 1; ...'. Values
    of fields named as parameters of a constructor of the parent are its
    arguments.
    """
    calls = []
    for parent_offset, parent in class_type.other_parents:
        values = _collect_parent_fields_values(
            proc_info, parent_offset, removed)
        if not values:
            continue
        call = _make_parent_construction(proc_info, parent, values)
        if call is not None:
            calls.append(call)
    return calls


def _collect_parent_fields_values(proc_info, parent_offset, instrs):
    """Return constant values assigned to fields of parent by offsets."""
    parent_ptrs = set()
    values = {}
    for instr in instrs:
        if not isinstance(instr, instructions.Assignment):
            continue
        dst, src = instr.dst, instr.src
        if (
            isinstance(dst, expressions.intermediate.Stackvar) and
            _is_this_with_offset(proc_info, src, parent_offset)
        ):
            parent_ptrs.add(dst.offset)
        elif (
            isinstance(dst, expressions.intermediate.Access) and
            isinstance(dst.expression, expressions.intermediate.Stackvar) and
            dst.expression.offset in parent_ptrs and
            isinstance(src, expressions.Constant)
        ):
            values[dst.offset] = src.value
    return values


def _is_this_with_offset(proc_info, e, offset):
    if not isinstance(e, expressions.Bin) or e.operator != Operator.ADD:
        return False
    right = e.right
    if not isinstance(right, expressions.Constant) or right.value != offset:
        return False
    this = e.left
    while isinstance(
        this, (expressions.ReinterpretCast, expressions.ImplicitCast)
    ):
        this = this.expression
    return proc_info.is_this_expression(this)


def _make_parent_construction(proc_info, parent, values):
    fields_by_name = dict(
        (name, offset) for offset, (data_type, name)
        in parent.get_all_fields().items()
    )
    for constructor in parent.constructors:
        parameters = list(constructor.get_parameters_ids().values())[1:]
        offsets = [fields_by_name.get(p.name) for p in parameters]
        if any(offset not in values for offset in offsets):
            continue
        arguments = [
            expressions.Constant(p.data_type, values[offset])
            for p, offset in zip(parameters, offsets)
        ]
        default_values = parent.get_default_values(constructor) or []
        # Arguments equal to default values are omitted
        while arguments and len(default_values) >= len(arguments) and (
            _parse_default_value(default_values[len(arguments) - 1]) ==
            arguments[-1].value
        ):
            arguments.pop()
            parameters.pop()
        if not arguments:
            return None
        proc_decl = ProcedureDeclaration(
            parent.class_name, CallingConvention.THISCALL, parent,
            [(p.data_type, p.name) for p in parameters], None)
        this = _find_this(proc_info)
        return instructions.CodeInstruction(expressions.ProcedureCall(
            name=parent.class_name, is_method=True,
            arguments=[this] + arguments, proc_decl=proc_decl))
    return None


def _parse_default_value(value):
    if value is None:
        return None
    if value in ("true", "TRUE"):
        return 1
    if value in ("false", "FALSE", "NULL", "nullptr"):
        return 0
    try:
        return int(value, 0)
    except ValueError:
        return None


def _find_this(proc_info):
    return next(iter(proc_info.stack_variables.values()))


def _find_base_destruction(proc_info, class_type, instrs):
    """Find start of inlined destructors of base classes.

    Destructors of base classes start with assignments of their tables.
    Their code may have labels if it isn't jumped to from the code of the
    destructor. The destructor itself starts with assignments of its own
    tables (the secondary tables of multiple inheritance too), they are
    skipped.
    """
    first = 1
    while first < len(instrs) and _is_secondary_vtbl_assign(
        proc_info, class_type, instrs[first]
    ):
        first += 1
    for start in range(first, len(instrs)):
        instr = instrs[start]
        if (
            extract_vtbl_addr_from_assign(proc_info, instr) is not None or
            _is_secondary_vtbl_assign(proc_info, class_type, instr) or
            _is_parent_destruction_start(proc_info, class_type, instrs, start)
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


def _is_parent_destruction_start(proc_info, class_type, instrs, index):
    """Check for start of inlined destructor of other parent.

    The pointer to other parent is checked for null before its destructor:

        p = this != nullptr ? this + offset : nullptr;
        p->vftable = parent::vftable;
    """
    offset = _parent_pointer_check_offset(proc_info, class_type, instrs[index])
    if offset is None or index + 1 >= len(instrs):
        return False
    instr = instrs[index + 1]
    if not isinstance(instr, instructions.Assignment):
        return False
    dst = instr.dst
    return (
        isinstance(dst, expressions.intermediate.Access) and
        dst.offset == 0 and dst.size == 4 and
        isinstance(dst.expression, expressions.intermediate.Stackvar) and
        dst.expression.offset == offset and
        isinstance(instr.src, expressions.intermediate.Global)
    )


def _parent_pointer_check_offset(proc_info, class_type, instr):
    """Return offset of variable of pointer to other parent checked for null.

        if (this != nullptr) p = this + offset; else p = 0;
    """
    if not isinstance(instr, instructions.IfInstruction):
        return None
    if instr.else_block is None:
        return None
    if len(instr.if_block) != 1 or len(instr.else_block) != 1:
        return None
    parent_ass, null_ass = instr.if_block[0], instr.else_block[0]
    if not isinstance(parent_ass, instructions.Assignment):
        return None
    if not isinstance(null_ass, instructions.Assignment):
        return None
    var = parent_ass.dst
    if (
        not isinstance(var, expressions.intermediate.Stackvar) or
        not isinstance(null_ass.dst, expressions.intermediate.Stackvar) or
        null_ass.dst.offset != var.offset
    ):
        return None
    if not any(
        _is_this_with_offset(proc_info, parent_ass.src, parent_offset)
        for parent_offset, parent in class_type.other_parents
    ):
        return None
    return var.offset


def _replace_parent_pointers(proc_info, class_type, instrs):
    """Call methods of other parents with this instead of its pointer.

    Visual C++ calls a method of other parent with a pointer to the parent:
    'p = this + offset; p->Method();' is 'this->Method();'.
    """
    pointers = set()
    result = []
    for instr in instrs:
        if (
            isinstance(instr, instructions.Assignment) and
            isinstance(instr.dst, expressions.intermediate.Stackvar) and
            any(
                _is_this_with_offset(proc_info, instr.src, parent_offset)
                for parent_offset, parent in class_type.other_parents
            )
        ):
            pointers.add(instr.dst.offset)
            continue
        if isinstance(instr, instructions.CodeInstruction):
            pc = instr.expression
            if (
                isinstance(pc, expressions.ProcedureCall) and
                pc.is_method and pc.arguments and
                isinstance(pc.arguments[0], expressions.intermediate.Stackvar)
                and pc.arguments[0].offset in pointers
            ):
                instr = instructions.CodeInstruction(pc.copy(
                    arguments=[_find_this(proc_info)] + pc.arguments[1:]))
        result.append(instr)
    if any(_uses_pointer(instr, pointers) for instr in result):
        return instrs
    return result


def _uses_pointer(instr, pointers):
    found = []

    def on_visit(e, **kwargs):
        if (
            isinstance(e, expressions.intermediate.Stackvar) and
            e.offset in pointers
        ):
            found.append(e)

    instr.visit(on_visit)
    return bool(found)


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
