import unittest

from calling_convention import CallingConvention
import data_types
import expressions
import instructions
from patterns.high_level.local_constructions import \
    restore_local_constructions
from procedure_declaration import ProcedureDeclaration
from tests.builder import i32_id
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)


def _point():
    point = data_types.ClassType("B_Point", {
        0: (data_types.Int32(), "x"),
        4: (data_types.Int32(), "y"),
    })
    point.add_constructor(ProcedureDeclaration(
        "B_Point", CallingConvention.THISCALL, point,
        [(data_types.Int32(), "x"), (data_types.Int32(), "y")], None))
    return point


def _emit(instrs):
    writer = Writer()
    procedure = restore_local_constructions(_Procedure(instrs))
    for instr in procedure.instructions:
        instr.emit_code(writer)
    return writer.get_string()


def _assign_field(var, field_name, value):
    return instructions.Assignment(
        expressions.FieldAccess(expressions.AddressOf(var), field_name),
        value)


class TestLocalConstructions(unittest.TestCase):
    def test_construction(self):
        p = expressions.Identifier(_point(), "p")
        self.assertEqual("B_Point p(a, b);\n", _emit([
            instructions.VariableDeclaration(p, None),
            _assign_field(p, "x", i32_id("a")),
            _assign_field(p, "y", i32_id("b")),
        ]))

    def test_not_all_fields(self):
        p = expressions.Identifier(_point(), "p")
        self.assertIn("B_Point p;\n", _emit([
            instructions.VariableDeclaration(p, None),
            _assign_field(p, "x", i32_id("a")),
        ]))
