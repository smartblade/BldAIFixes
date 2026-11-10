import data_types
import expressions
import instructions

from .convert_return_value_to_bool import convert_return_value_to_bool
from .convert_to_implicit_cast import convert_to_implicit_cast


def transform_returns(proc_info, proc_decl, characteristics, instrs):
    instrs = _rewrite_returns(proc_decl, characteristics, instrs)
    instrs = _eliminate_unnecessary_returns(proc_info, proc_decl, instrs)
    return instrs


def _is_this_dereference(proc_info, e):
    if not isinstance(e, expressions.MakeReference):
        return False
    deref = e.expression
    if not isinstance(deref, expressions.Dereference):
        return False
    return proc_info.is_this_expression(deref.expression)


def _eliminate_unnecessary_returns(proc_info, proc_decl, instrs):
    ri = instrs[-1]
    if isinstance(ri, instructions.ReturnInstruction):
        if (
            ri.expression is None or
            proc_decl is not None and
            proc_decl.is_constructor and
            _is_this_dereference(proc_info, ri.expression)
        ):
            instrs.pop()
    elif isinstance(instrs[-1], instructions.LabeledBlock):
        block_instructions = _eliminate_unnecessary_returns(
            proc_info, proc_decl, instrs[-1].instructions)
        instrs[-1] = instructions.LabeledBlock(
            instrs[-1].label, block_instructions)
    return instrs


def _rewrite_returns(proc_decl, characteristics, instrs):
    new_instructions = []
    i = 0
    while i < len(instrs):
        instr = instrs[i]
        if i + 1 < len(instrs):
            next_instr = instrs[i + 1]
        else:
            next_instr = None
        instr = _rewrite_nested_blocks(proc_decl, characteristics, instr)
        updated_instrs = _rewrite_return(
            proc_decl, characteristics, instr, next_instr)
        if updated_instrs:
            new_instructions.extend(updated_instrs)
            i += 2
            continue
        updated_instrs = _rewrite_return_from_last_call(
            proc_decl, characteristics, instr, next_instr)
        if updated_instrs:
            new_instructions.extend(updated_instrs)
            i += 2
            continue
        if next_instr is None and isinstance(instr, instructions.LabeledBlock):
            instr = instructions.LabeledBlock(
                instr.label, _rewrite_returns(
                    proc_decl, characteristics, instr.instructions))
        new_instructions.append(instr)
        i += 1
    return new_instructions


def _rewrite_nested_blocks(proc_decl, characteristics, instr):
    instr = _rewrite_if(proc_decl, characteristics, instr)
    instr = _rewrite_while(proc_decl, characteristics, instr)
    return instr


def _rewrite_if(proc_decl, characteristics, instr):
    if isinstance(instr, instructions.IfInstruction):
        if_block = _rewrite_returns(proc_decl, characteristics, instr.if_block)
        else_block = None
        if instr.else_block is not None:
            else_block = _rewrite_returns(
                proc_decl, characteristics, instr.else_block)
        return instructions.IfInstruction(
            instr.if_clause, if_block, else_block)
    return instr


def _rewrite_while(proc_decl, characteristics, instr):
    if isinstance(instr, instructions.WhileInstruction):
        block = _rewrite_returns(proc_decl, characteristics, instr.block)
        return instructions.WhileInstruction(instr.clause, block)
    return instr


def _rewrite_return(proc_decl, characteristics, regdef, return_instr):
    if not isinstance(regdef, instructions.TemporaryRegisterDefinition):
        return
    if not isinstance(return_instr, instructions.ReturnInstruction):
        return
    if return_instr.expression is not None:
        return
    if proc_decl is None:
        return
    if proc_decl.return_type is None:
        return
    data_type = proc_decl.return_type
    if _is_eax_return_type(data_type):
        return_value = regdef.pop_reg_value("eax")
    elif _is_al_return_type(data_type):
        return_value = regdef.pop_reg_value("al")
    elif _is_fpu_return_type(data_type) and regdef.has_fpu_values():
        # Floating point values are returned in ST(0) as double, 'return'
        # converts them to float
        return_value = regdef.pop_fpu()
    else:
        return
    if not _is_fpu_return_type(data_type):
        return_value = expressions.do_reinterpret(data_type, return_value)
    return_value = convert_return_value_to_bool(
        proc_decl, characteristics, return_value)
    return_value = convert_to_implicit_cast(return_value, data_type)
    new_instructions = []
    if not regdef.is_empty():
        new_instructions.append(regdef)
    new_instructions.append(instructions.ReturnInstruction(return_value))
    return new_instructions


def _rewrite_return_from_last_call(
    proc_decl, characteristics, instr, return_instr
):
    if not isinstance(instr, instructions.CodeInstruction):
        return
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return
    if not isinstance(return_instr, instructions.ReturnInstruction):
        return
    if return_instr.expression is not None:
        return
    if pc.proc_decl is None:
        return
    last_call_data_type = pc.proc_decl.return_type
    if last_call_data_type is None:
        return
    if proc_decl is None:
        data_type = last_call_data_type
        is_eax_return = True
    else:
        data_type = proc_decl.return_type
        is_eax_return = _is_eax_return_type(data_type)
    if not _is_eax_return_type(last_call_data_type) or not is_eax_return:
        return
    return_value = expressions.do_reinterpret(data_type, pc)
    return_value = convert_return_value_to_bool(
        proc_decl, characteristics, return_value)
    new_instructions = [instructions.ReturnInstruction(return_value)]
    return new_instructions


def _is_eax_return_type(data_type):
    return (
        isinstance(data_type, data_types.Pointer32) or
        isinstance(data_type, data_types.Reference) or
        isinstance(data_type, data_types.Int32) or
        isinstance(data_type, data_types.Long32) or
        isinstance(data_type, data_types.UInt32)
    )


def _is_al_return_type(data_type):
    return (
        isinstance(data_type, data_types.Char) or
        isinstance(data_type, data_types.UChar)
    )


def _is_fpu_return_type(data_type):
    return isinstance(data_type, (data_types.Double, data_types.Float))
