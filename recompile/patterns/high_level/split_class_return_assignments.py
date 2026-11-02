import data_types
import expressions
from expressions.operator import Operator
from expression_transformer import ExpressionTransformer
import instructions


def split_class_return_assignments(procedure):
    """Split assignments of objects returned by value from expressions.

    An object returned by value is constructed by the called procedure in
    a variable: 'x = f()'. If such an assignment is an argument of a call
    without other side effects, 'g(x = f())', it is moved before the call:
    'x = f(); g(x);'. Assignments to variables are declarations with
    initialization later: 'B_Vector x = f();'.
    """
    return procedure.transform(_Splitter())


class _Splitter(ExpressionTransformer):
    def pre_transform_block_instructions(self, block_instructions, **kwargs):
        chain = block_instructions.interval(0)
        instr = chain.as_instr(0)
        new_instructions = _split(instr)
        if new_instructions is not None:
            chain.replace_instructions(new_instructions)


def _split(instr):
    if not isinstance(instr, instructions.CodeInstruction):
        return None
    e = instr.expression
    var = _get_assigned_variable(e)
    if var is not None:
        return [instructions.Assignment(var, e.right)]
    if not isinstance(e, expressions.ProcedureCall):
        return None
    assignments = [
        (i, arg) for i, arg in enumerate(e.arguments)
        if _get_assigned_variable(arg) is not None
    ]
    if len(assignments) != 1:
        return None
    index, assignment = assignments[0]
    other_arguments = e.arguments[:index] + e.arguments[index + 1:]
    if any(_has_side_effects(arg) for arg in other_arguments):
        return None
    if e.callee_expression is not None and _has_side_effects(
        e.callee_expression
    ):
        return None
    var = _get_assigned_variable(assignment)
    arguments = list(e.arguments)
    arguments[index] = assignment.left
    return [
        instructions.Assignment(var, assignment.right),
        instructions.CodeInstruction(e.copy(arguments=arguments)),
    ]


def _get_assigned_variable(e):
    """Return variable of class assigned from call returning object."""
    if not isinstance(e, expressions.Bin) or e.operator != Operator.ASS:
        return None
    if not isinstance(e.right, expressions.ProcedureCall):
        return None
    var = e.left
    if isinstance(var, expressions.MakeReference):
        var = var.expression
    if not isinstance(var, expressions.Identifier):
        return None
    if not isinstance(var.data_type, data_types.ClassType):
        return None
    return var


def _has_side_effects(e):
    found = []

    def on_visit(sub_e, **kwargs):
        if isinstance(sub_e, expressions.ProcedureCall):
            found.append(sub_e)
        elif isinstance(sub_e, expressions.Bin) and sub_e.operator in (
            Operator.ASS, Operator.ADD_ASS, Operator.SUB_ASS
        ):
            found.append(sub_e)

    e.visit(on_visit)
    return bool(found)
