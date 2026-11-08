import data_types
import expressions
from expressions.operator import Operator
import instructions
from .goto_eliminator.collect_label_uses import collect_label_uses


def collapse_inlined_clears(procedure):
    """Collapse inlined 'void Clear(int deleteItems)' of arrays into calls.

    Visual C++ inlines the method of B_PtrArray:
        if (a.num_alloc == 0) goto end;
        if (deleteItems == 0) goto skip;
        for (i = 0; i < a.size; i++) delete a.elements[i];
    skip:
        t = a.elements; operator delete(t);
        a.elements = 0; a.size = 0; a.num_alloc = 0;
    end:
    The code is collapsed into 'a.Clear(deleteItems)' if the labels are
    used by the inlined code only. A constant argument is a boolean.
    """
    label_uses = collect_label_uses(procedure.instructions)
    instrs = _collapse_block(list(procedure.instructions), label_uses)
    return procedure.copy(instrs=instrs)


def _collapse_block(block, label_uses):
    block = [_collapse_nested(instr, label_uses) for instr in block]
    new_block = []
    i = 0
    while i < len(block):
        collapsed = _try_collapse(block, i, label_uses)
        if collapsed is not None:
            new_block.extend(collapsed)
            i += 4
            continue
        new_block.append(block[i])
        i += 1
    return new_block


def _collapse_nested(instr, label_uses):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _collapse_block(else_block, label_uses)
        return instructions.IfInstruction(
            instr.if_clause, _collapse_block(instr.if_block, label_uses),
            else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _collapse_block(instr.block, label_uses))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _collapse_block(instr.instructions, label_uses))
    return instr


def _try_collapse(block, index, label_uses):
    if index + 4 > len(block):
        return None
    check_alloc, check_delete, loop, skip_block = block[index:index + 4]
    end_label = _goto_if(check_alloc)
    skip_label = _goto_if(check_delete)
    if end_label is None or skip_label is None:
        return None
    obj = _compared_field(check_alloc.if_clause, "num_alloc")
    if obj is None:
        return None
    delete_items = _delete_items_argument(check_delete.if_clause)
    if delete_items is None:
        return None
    if not isinstance(loop, instructions.ForInstruction):
        return None
    if len(loop.block) != 1 or not isinstance(
        loop.block[0], instructions.Delete
    ):
        return None
    if not isinstance(skip_block, instructions.LabeledBlock):
        return None
    if skip_block.label != skip_label:
        return None
    skip_instrs = skip_block.instructions
    if len(skip_instrs) != 6 or not _is_freeing(skip_instrs[:5], obj):
        return None
    end_block = skip_instrs[5]
    if not isinstance(end_block, instructions.LabeledBlock):
        return None
    if end_block.label != end_label:
        return None
    if len(label_uses.get(end_label, ())) != 1:
        return None
    if len(label_uses.get(skip_label, ())) != 1:
        return None
    call = _make_clear_call(obj, delete_items)
    if call is None:
        return None
    return [instructions.CodeInstruction(call)] + end_block.instructions


def _goto_if(instr):
    if not isinstance(instr, instructions.IfInstruction):
        return None
    if instr.else_block or len(instr.if_block) != 1:
        return None
    goto = instr.if_block[0]
    if not isinstance(goto, instructions.Goto):
        return None
    return goto.label


def _compared_field(clause, field_name):
    """Object of 'obj->field == 0'."""
    if not isinstance(clause, expressions.Bin) or clause.operator != Operator.EQ:
        return None
    if not _is_zero(clause.right):
        return None
    left = clause.left
    if not isinstance(left, expressions.FieldAccess):
        return None
    if left.field_name != field_name:
        return None
    return left.expression


def _delete_items_argument(clause):
    """Argument of 'deleteItems == 0' checked by the inlined method."""
    if not isinstance(clause, expressions.Bin) or clause.operator != Operator.EQ:
        return None
    if not _is_zero(clause.right):
        return None
    value = clause.left
    if isinstance(value, expressions.Constant):
        if value.value not in (0, 1):
            return None
        return expressions.Constant(data_types.Bool(), value.value)
    return value


def _is_freeing(instrs, obj):
    """Check for 't = obj->elements; operator delete(t); obj->elements = 0;
    obj->size = 0; obj->num_alloc = 0;'."""
    copy, delete, *resets = instrs
    if not isinstance(copy, instructions.Assignment):
        return False
    if not _is_field(copy.src, obj, "elements"):
        return False
    if not isinstance(delete, instructions.CodeInstruction):
        return False
    pc = delete.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return False
    if pc.name != "operator delete" or len(pc.arguments) != 1:
        return False
    if pc.arguments[0].emit_code() != copy.dst.emit_code():
        return False
    for reset, field_name in zip(resets, ("elements", "size", "num_alloc")):
        if not isinstance(reset, instructions.Assignment):
            return False
        if not _is_field(reset.dst, obj, field_name):
            return False
        if not _is_zero(reset.src):
            return False
    return True


def _is_field(e, obj, field_name):
    return (
        isinstance(e, expressions.FieldAccess) and
        e.field_name == field_name and
        e.expression.emit_code() == obj.emit_code()
    )


def _is_zero(e):
    if e is expressions.Null:
        return True
    return isinstance(e, expressions.Constant) and e.value == 0


def _make_clear_call(obj, delete_items):
    obj_type = obj.data_type
    if not isinstance(obj_type, data_types.Pointer32):
        return None
    class_type = obj_type.pointee
    if not isinstance(class_type, data_types.ClassType):
        return None
    method = None
    for cur_class in (class_type, class_type.template):
        if cur_class is not None and method is None:
            method = cur_class.find_other_method("Clear")
    if method is None:
        return None
    return expressions.ProcedureCall(
        name="Clear", is_method=True, proc_decl=method,
        arguments=[obj, delete_items])
