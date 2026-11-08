import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.goto_eliminator import transform_forward_gotos
from writer import Writer


def _id(name):
    return expressions.Identifier(data_types.Int32(), name)


def _emit(instrs):
    writer = Writer()
    for instr in instrs:
        instr.emit_code(writer)
    return writer.get_string()


class TestForwardGotos(unittest.TestCase):
    def test_goto_over_returning_code(self):
        clause = expressions.Bin(
            Operator.GE, _id("a"), expressions.Constant(data_types.Int32(), 8))
        instrs = [
            instructions.IfInstruction(clause, [instructions.Goto("l")]),
            instructions.Assignment(_id("b"), _id("a")),
            instructions.ReturnInstruction(_id("b")),
            instructions.LabeledBlock("l", [
                instructions.ReturnInstruction(_id("a"))]),
        ]
        self.assertEqual(
            "if (a < 8)\n{\n    b = a;\n    return b;\n}\n"
            "else\n{\n    return a;\n}\n",
            _emit(transform_forward_gotos(instrs, {})))

    def test_code_not_returning(self):
        clause = expressions.Bin(
            Operator.GE, _id("a"), expressions.Constant(data_types.Int32(), 8))
        instrs = [
            instructions.IfInstruction(clause, [instructions.Goto("l")]),
            instructions.Assignment(_id("b"), _id("a")),
            instructions.LabeledBlock("l", [
                instructions.ReturnInstruction(_id("a"))]),
        ]
        self.assertIn("goto l;", _emit(transform_forward_gotos(instrs, {})))
