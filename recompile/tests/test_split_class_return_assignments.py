import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.split_class_return_assignments import _split
from tests.builder import i32_id


def _vector_id(name):
    vector = data_types.ClassType("B_Vector", {0: (data_types.Double(), "x")})
    return expressions.Identifier(vector, name)


def _assignment(var):
    return expressions.Bin(
        Operator.ASS, expressions.MakeReference(var),
        expressions.ProcedureCall(name="f", arguments=[]))


class TestSplitClassReturnAssignments(unittest.TestCase):
    def test_assignment(self):
        var = _vector_id("v")
        instrs = _split(instructions.CodeInstruction(_assignment(var)))
        self.assertEqual(1, len(instrs))
        self.assertIs(var, instrs[0].dst)
        self.assertEqual("f()", instrs[0].src.emit_code())

    def test_assignment_in_argument(self):
        var = _vector_id("v")
        call = expressions.ProcedureCall(
            name="g", arguments=[_assignment(var), i32_id("a")])
        instrs = _split(instructions.CodeInstruction(call))
        self.assertEqual(2, len(instrs))
        self.assertEqual("g(v, a)", instrs[1].expression.emit_code())

    def test_argument_with_side_effects(self):
        var = _vector_id("v")
        call = expressions.ProcedureCall(name="g", arguments=[
            _assignment(var), expressions.ProcedureCall(name="h")])
        self.assertIsNone(_split(instructions.CodeInstruction(call)))
