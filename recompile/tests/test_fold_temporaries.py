import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.fold_temporaries import fold_temporaries
from tests.builder import i32_id
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)


def _point():
    return data_types.ClassType("B_Point", {
        0: (data_types.Int32(), "x"),
        4: (data_types.Int32(), "y"),
    })


def _emit(instrs):
    declared_types = {"B_Point": _point()}
    writer = Writer()
    procedure = fold_temporaries(_Procedure(instrs), declared_types)
    for instr in procedure.instructions:
        instr.emit_code(writer)
    return writer.get_string()


def _construction(*arguments):
    return expressions.ProcedureCall(
        name="B_Point", is_method=False, arguments=list(arguments))


class TestFoldTemporaries(unittest.TestCase):
    def test_constructor_arguments(self):
        t = expressions.Identifier(data_types.Int32(), "unknown_loc_08")
        self.assertEqual("return B_Point(a + b, c);\n", _emit([
            instructions.VariableDeclaration(
                t, expressions.Bin(Operator.ADD, i32_id("a"), i32_id("b"))),
            instructions.ReturnInstruction(_construction(t, i32_id("c"))),
        ]))

    def test_temporary_object_argument(self):
        point = _point()
        t = expressions.Identifier(point, "unknown_loc_10")
        call = expressions.ProcedureCall(
            name="f", arguments=[expressions.MakeReference(t)])
        self.assertEqual("f(B_Point(a, b));\n", _emit([
            instructions.VariableDeclaration(
                t, _construction(i32_id("a"), i32_id("b")),
                is_direct_initialization=True),
            instructions.CodeInstruction(call),
        ]))

    def test_named_variable(self):
        t = expressions.Identifier(data_types.Int32(), "x")
        self.assertIn("int x = a;", _emit([
            instructions.VariableDeclaration(t, i32_id("a")),
            instructions.ReturnInstruction(_construction(t, i32_id("c"))),
        ]))
