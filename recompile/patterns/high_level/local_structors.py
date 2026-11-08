import data_types
import expressions
from expressions.operator import Operator
import instructions
from .goto_eliminator.collect_label_uses import collect_label_uses
from .inlined_base_structors import _parse_default_value
from .inlined_clear import _compared_field, _goto_if, _is_freeing


def remove_inlined_local_structors(procedure, stack_vars):
    """Remove inlined constructors and destructors of local arrays.

    A local object of a class with virtual methods constructed by an
    inlined constructor with default arguments is initialized field by
    field, then the table of virtual methods is set:
        a.elements = 0; a.size = 0; a.increment = 16; a.num_alloc = 0;
        a.deleteItems = 1; vftable(a) = B_PtrArray::vftable;
    The inlined destructor of B_PtrArray at the end of the scope sets the
    table and clears the array by its 'deleteItems':
        vftable(a) = B_PtrArray::vftable;
        if (a.num_alloc == 0) goto end;
        d = a.deleteItems;
        if (a.num_alloc == 0) goto end;
        if (d == 0) goto skip;
        for (...) delete a.elements[i];
    skip:
        t = a.elements; operator delete(t); a.elements = 0; ...
    end:
    Both are implicit in C++: 'B_PtrArray<B_Sector> a;' and the end of the
    scope.
    """
    variables = dict(
        (offset, var) for offset, var in stack_vars.items()
        if isinstance(var.data_type, data_types.ClassType) and
        var.data_type.has_virtual_methods
    )
    if not variables:
        return procedure
    label_uses = collect_label_uses(procedure.instructions)
    instrs = _remove_block(
        list(procedure.instructions), variables, label_uses)
    return procedure.copy(instrs=instrs)


def _remove_block(block, variables, label_uses):
    block = [_remove_nested(instr, variables, label_uses) for instr in block]
    new_block = []
    i = 0
    while i < len(block):
        length = _construction_length(block, i, variables)
        if length:
            i += length
            continue
        result = _destruction(block, i, variables, label_uses)
        if result is not None:
            rest, length = result
            new_block.extend(rest)
            i += length
            continue
        new_block.append(block[i])
        i += 1
    return new_block


def _remove_nested(instr, variables, label_uses):
    def remove(block):
        return _remove_block(block, variables, label_uses)

    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = remove(else_block)
        return instructions.IfInstruction(
            instr.if_clause, remove(instr.if_block), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, remove(instr.block))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, remove(instr.instructions))
    return instr


def _construction_length(block, index, variables):
    """Length of the inlined construction by default arguments or 0."""
    for offset, var in variables.items():
        class_type = var.data_type
        fields = sorted(class_type.get_all_fields().items())
        count = len(fields)
        if index + count >= len(block):
            continue
        values = {}
        for instr, (field_offset, (field_type, name)) in zip(
            block[index:index + count], fields
        ):
            if not isinstance(instr, instructions.Assignment):
                break
            if not _is_variable_field(instr.dst, var, name):
                break
            value = _constant_value(instr.src)
            if value is None:
                break
            values[name] = value
        else:
            if not _is_vtable_assignment(block[index + count], offset):
                continue
            if not _are_default_values(class_type, values):
                continue
            return count + 1
    return 0


def _destruction(block, index, variables, label_uses):
    """Return (instructions after the inlined destructor, its length)."""
    for offset, var in variables.items():
        if not _is_vtable_assignment(block[index], offset):
            continue
        obj = expressions.AddressOf(var)
        tail = block[index + 1:]
        if len(tail) != 6:
            continue
        check, copy, check_alloc, check_delete, loop, skip_block = tail[:6]
        end_label = _goto_if(check)
        if end_label is None or _goto_if(check_alloc) != end_label:
            continue
        for alloc_check in (check, check_alloc):
            checked = _compared_field(alloc_check.if_clause, "num_alloc")
            if checked is None or checked.emit_code() != obj.emit_code():
                break
        else:
            if not (
                isinstance(copy, instructions.Assignment) and
                _is_variable_field(copy.src, var, "deleteItems")
            ):
                continue
            skip_label = _goto_if(check_delete)
            clause = check_delete.if_clause
            if (
                skip_label is None or
                not isinstance(clause, expressions.Bin) or
                clause.operator != Operator.EQ or
                clause.left.emit_code() != copy.dst.emit_code()
            ):
                continue
            if not isinstance(loop, instructions.ForInstruction):
                continue
            if not isinstance(skip_block, instructions.LabeledBlock):
                continue
            if skip_block.label != skip_label:
                continue
            skip_instrs = skip_block.instructions
            if len(skip_instrs) != 6:
                continue
            if not _is_freeing(skip_instrs[:5], obj):
                continue
            end_block = skip_instrs[5]
            if not isinstance(end_block, instructions.LabeledBlock):
                continue
            if end_block.label != end_label:
                continue
            if len(label_uses.get(end_label, ())) != 2:
                continue
            if len(label_uses.get(skip_label, ())) != 1:
                continue
            return end_block.instructions, 7
    return None


def _is_variable_field(e, var, name):
    if not isinstance(e, expressions.FieldAccess) or e.field_name != name:
        return False
    obj = e.expression
    if isinstance(obj, expressions.AddressOf):
        obj = obj.expression
    return isinstance(obj, expressions.Identifier) and obj.name == var.name


def _constant_value(e):
    if e is expressions.Null:
        return 0
    if isinstance(e, expressions.Constant) and isinstance(e.value, int):
        return e.value
    return None


def _is_vtable_assignment(instr, offset):
    if not isinstance(instr, instructions.Assignment):
        return False
    dst = instr.dst
    if not isinstance(dst, expressions.intermediate.Stackvar):
        return False
    if dst.offset != offset or dst.size != 4:
        return False
    return isinstance(instr.src, expressions.intermediate.Global)


def _are_default_values(class_type, values):
    """Check that the fields have values of a constructor called without
    arguments: parameters initialize the fields of the same names, other
    fields are zero."""
    for constructor in class_type.constructors:
        parameters = list(constructor.get_parameters_ids().values())[1:]
        default_values = class_type.get_default_values(constructor) or []
        if len(default_values) != len(parameters):
            continue
        expected = dict((name, 0) for name in values)
        for parameter, default_value in zip(parameters, default_values):
            if parameter.name not in values:
                break
            expected[parameter.name] = _parse_default_value(default_value)
        else:
            if expected == values:
                return True
    return False
