import data_types
import expressions
from expressions.operator import Operator
import instructions

from .apply_characteristics import apply_characteristics_to_assignment
from .is_int_constant import is_int_constant
from .is_refcnt_assignment import is_refcnt_assignment
from .obj_from_field_access import try_extract_obj_from_field_access
from .tmp_stack_obj import transform_tmp_stack_obj


def transform_block_instructions(block_instructions, **kwargs):
    instr = block_instructions.get_current_instruction()
    cb = _cb_by_instruction_type.get(type(instr))
    if cb is None:
        return
    cb(block_instructions, instr, **kwargs)


def _transform_assignment(block_instructions, assignment, **kwargs):
    dst = assignment.dst
    if not isinstance(dst, expressions.intermediate.Stackvar):
        return
    src = assignment.src
    apply_characteristics_to_assignment(block_instructions, dst, src, **kwargs)


def _transform_if_instruction(block_instructions, if_instr, **kwargs):
    if not isinstance(if_instr.if_clause, expressions.Bin):
        return
    if if_instr.if_clause.operator == Operator.NE:
        _transform_ne_if_instruction(block_instructions, if_instr, **kwargs)
    elif if_instr.if_clause.operator == Operator.EQ:
        _transform_eq_if_instruction(block_instructions, if_instr, **kwargs)


def _transform_code_instruction(block_instructions, code_instr, **kwargs):
    pc = code_instr.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return
    transform_tmp_stack_obj(block_instructions, code_instr, **kwargs)


def _transform_ne_if_instruction(
    block_instructions, if_instr, inline_procedures, stack_vars, **kwargs
):
    if len(if_instr.if_block) < 3:
        return
    deleting_if = if_instr.if_block[-2]
    if not isinstance(deleting_if, instructions.IfInstruction):
        return
    if len(deleting_if.if_block) != 1:
        return
    deleting_instr = deleting_if.if_block[0]
    if not isinstance(deleting_instr, instructions.CodeInstruction):
        return
    deleting_call = deleting_instr.expression
    if not isinstance(deleting_call, expressions.ProcedureCall):
        return
    if deleting_call.name not in _operator_delete_names:
        return
    deleting_offset = _extract_argument_offset(deleting_call)
    if deleting_offset is None:
        return
    if deleting_if.else_block is not None:
        return
    if not _check_deleting_clause(deleting_if.if_clause):
        return
    deleting_result_ass = if_instr.if_block[-1]
    if not isinstance(deleting_result_ass, instructions.Assignment):
        return
    deleting_result_offset = _extract_var_offset(deleting_result_ass.dst)
    if not _check_var_offset(deleting_result_ass.src, deleting_offset):
        return
    if if_instr.else_block is None:
        return
    if len(if_instr.else_block) != 1:
        return
    deleting_result_ass_null = if_instr.else_block[0]
    if not isinstance(deleting_result_ass_null, instructions.Assignment):
        return
    if not _check_var_offset(
        deleting_result_ass_null.dst, deleting_result_offset
    ):
        return
    if not _is_unknown_constant(deleting_result_ass_null.src, 0):
        return
    if not _is_deleting_obj_null_check(if_instr.if_clause, deleting_offset):
        return
    deleting_chain = block_instructions.interval(-2)
    first_ass = deleting_chain.as_instr(0, instructions.Assignment)
    if first_ass is None:
        return
    deleting_obj_copy_offset = _extract_var_offset(first_ass.dst)
    if deleting_obj_copy_offset is None:
        return
    second_ass = deleting_chain.as_instr(1, instructions.Assignment)
    if second_ass is None:
        return
    if not _check_var_offset(second_ass.dst, deleting_offset):
        return
    if not _check_var_offset(second_ass.src, deleting_obj_copy_offset):
        return
    assert deleting_chain.as_instr(2, instructions.IfInstruction) == if_instr
    stack_vars[deleting_offset] = expressions.Identifier(
        data_types.Pointer32(), "__deleting_obj")
    stack_vars[deleting_obj_copy_offset] = expressions.Identifier(
        data_types.Pointer32(), "__deleting_obj_copy")
    stack_vars[deleting_result_offset] = expressions.Identifier(
        data_types.Pointer32(), "__deleting_result")
    deleting_expression = first_ass.src
    destructor_instructions = if_instr.if_block[:-2]
    destructor_class = _extract_destructor_class(
        destructor_instructions, deleting_offset)
    if destructor_class is not None:
        deleting_expression = expressions.do_reinterpret(
            data_types.Pointer32(destructor_class), deleting_expression)
    elif (
        isinstance(deleting_expression.data_type, data_types.Pointer32) and
        isinstance(deleting_expression.data_type.pointee, data_types.ClassType)
    ):
        destructor_class = deleting_expression.data_type.pointee
        inline_procedures.add_destructor(
            destructor_class, deleting_offset, destructor_instructions)
    else:
        return
    deleting_chain.replace_instructions(
        [instructions.Delete(deleting_expression)])


def _transform_eq_if_instruction(block_instructions, if_instr, **kwargs):
    if_clause = if_instr.if_clause
    if not is_int_constant(if_clause.right, 0):
        return None
    obj = try_extract_obj_from_field_access(if_clause.left, "ob_refcnt")
    if obj is None:
        return None
    if if_instr.else_block is not None:
        return None
    if len(if_instr.if_block) != 1:
        return None
    block_instr = if_instr.if_block[0]
    if not isinstance(block_instr, instructions.CodeInstruction):
        return None
    pc = block_instr.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return None
    ob_type = try_extract_obj_from_field_access(
        pc.callee_expression, "tp_dealloc")
    if ob_type is None:
        return None
    deleting_obj = try_extract_obj_from_field_access(ob_type, "ob_type")
    if deleting_obj is None:
        return None
    if obj.emit_code() != deleting_obj.emit_code():
        return None
    if len(pc.arguments) != 1:
        return None
    if obj.emit_code() != pc.arguments[0].emit_code():
        return None
    decref_chain = block_instructions.interval(-1)
    if not is_refcnt_assignment(decref_chain.as_instr(0), obj, 1, Operator.SUB):
        return None
    assert decref_chain.as_instr(1, instructions.IfInstruction) == if_instr
    decref = instructions.CodeInstruction(
        expressions.ProcedureCall(name="Py_DECREF", arguments=[obj]))
    decref_chain.replace_instructions([decref])


def _extract_argument_offset(pc):
    if len(pc.arguments) != 1:
        return None
    return _extract_var_offset(pc.arguments[0])


def _extract_var_offset(e):
    if not isinstance(e, expressions.intermediate.Stackvar):
        return None
    if e.size != 4:
        return None
    return e.offset


def _check_var_offset(e, offset):
    assert offset is not None
    return _extract_var_offset(e) == offset


def _check_deleting_clause(e):
    if not isinstance(e, expressions.Bin):
        return False
    if e.operator != Operator.NE:
        return False
    right = e.right
    if not is_int_constant(right, 0):
        return False
    left = e.left
    if not isinstance(left, expressions.Bin):
        return False
    if left.operator != Operator.BIT_AND:
        return False
    if not is_int_constant(left.left, 1):
        return False
    if not is_int_constant(left.right, 1):
        return False
    return True


def _is_deleting_obj_null_check(clause, var_offset):
    if not isinstance(clause, expressions.Bin):
        return False
    if clause.operator != Operator.NE:
        return False
    if not _is_unknown_constant(clause.right, 0):
        return False
    if not _check_var_offset(clause.left, var_offset):
        return False
    return True


def _extract_destructor_class(destructor_instructions, deleting_offset):
    if len(destructor_instructions) != 1:
        return None
    instruction = destructor_instructions[0]
    if not isinstance(instruction, instructions.CodeInstruction):
        return None
    pc = instruction.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return None
    if not pc.is_method:
        return None
    if len(pc.arguments) != 1:
        return None
    if pc.proc_decl is None:
        return None
    if not pc.proc_decl.is_destructor:
        return None
    arg = pc.arguments[0]
    if not isinstance(arg, expressions.ReinterpretCast):
        return None
    if not isinstance(arg.data_type, data_types.Pointer32):
        return None
    destructor_class = arg.data_type.pointee
    assert destructor_class == pc.proc_decl.method_class
    if not _check_var_offset(arg.expression, deleting_offset):
        return None
    return destructor_class


def _is_unknown_constant(e, int_value):
    if not isinstance(e, expressions.Constant):
        return False
    if not isinstance(e.data_type, data_types.Unknown32):
        return False
    if e.value != int_value:
        return False
    return True


# Names of operator delete: Visual C++ runtime and SmartHeap
_operator_delete_names = {"??3@YAXPAX@Z", "shi_delete"}

_cb_by_instruction_type = {
    instructions.IfInstruction: _transform_if_instruction,
    instructions.Assignment: _transform_assignment,
    instructions.CodeInstruction: _transform_code_instruction,
}
