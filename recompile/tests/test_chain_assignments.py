import unittest

import data_types
import expressions
import instructions
from patterns.high_level.chain_assignments import chain_assignments
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)


def _emit(instrs):
    writer = Writer()
    for instr in chain_assignments(_Procedure(instrs)).instructions:
        instr.emit_code(writer)
    return writer.get_string()


def _vector():
    return data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })


class TestChainAssignments(unittest.TestCase):
    def test_objects(self):
        vector = _vector()
        a = expressions.Identifier(vector, "a")
        b = expressions.Identifier(vector, "b")
        zero = expressions.Identifier(vector, "zero")
        self.assertEqual("b = a = zero;\n", _emit([
            instructions.Assignment(a, zero),
            instructions.Assignment(b, a),
        ]))

    def test_scalars(self):
        # 'b = a = x' doesn't read a again
        a = expressions.Identifier(data_types.Int32(), "a")
        b = expressions.Identifier(data_types.Int32(), "b")
        x = expressions.Identifier(data_types.Int32(), "x")
        self.assertEqual("a = x;\nb = a;\n", _emit([
            instructions.Assignment(a, x),
            instructions.Assignment(b, a),
        ]))

    def test_other_source(self):
        vector = _vector()
        a = expressions.Identifier(vector, "a")
        b = expressions.Identifier(vector, "b")
        c = expressions.Identifier(vector, "c")
        self.assertEqual("a = c;\nb = c;\n", _emit([
            instructions.Assignment(a, c),
            instructions.Assignment(b, c),
        ]))
