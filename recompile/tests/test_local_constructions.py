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


def _box():
    box = data_types.ClassType("B_Box", {
        0: (data_types.Int32(), "a"),
        4: (data_types.Int32(), "b"),
    })
    box.add_constructor(ProcedureDeclaration(
        "B_Box", CallingConvention.THISCALL, box,
        [(data_types.Int32(), "a"), (data_types.Int32(), "b")], None))
    return box


def _call_constructor(var, *arguments):
    proc_decl = var.data_type.constructors[0]
    return instructions.CodeInstruction(expressions.ProcedureCall(
        name=var.data_type.class_name, is_method=True, proc_decl=proc_decl,
        arguments=[expressions.AddressOf(var)] + list(arguments)))


class TestCalledLocalConstructions(unittest.TestCase):
    """'T v; v.T(args);' with a constructor that is not inlined."""

    def test_construction(self):
        b = expressions.Identifier(_box(), "b")
        self.assertEqual("B_Box b(x, y);\n", _emit([
            instructions.VariableDeclaration(b, None),
            _call_constructor(b, i32_id("x"), i32_id("y")),
        ]))

    def test_declarations_of_temporaries_are_kept(self):
        b = expressions.Identifier(_box(), "b")
        t = i32_id("t")
        self.assertEqual("int t;\nB_Box b(t, y);\n", _emit([
            instructions.VariableDeclaration(b, None),
            instructions.VariableDeclaration(t, None),
            _call_constructor(b, t, i32_id("y")),
        ]))

    def test_argument_uses_object(self):
        b = expressions.Identifier(_box(), "b")
        result = _emit([
            instructions.VariableDeclaration(b, None),
            _call_constructor(
                b, expressions.FieldAccess(expressions.AddressOf(b), "a"),
                i32_id("y")),
        ])
        self.assertTrue(result.startswith("B_Box b;\n"), result)
