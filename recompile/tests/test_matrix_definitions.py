import unittest

import data_types
import expressions
import instructions
from expressions.do_pointer_dereference import do_pointer_dereference
from patterns.high_level.matrix_definitions import _collapse_block
from writer import Writer


def _this():
    matrix = data_types.ClassType("B_Matrix", {
        0: (data_types.Array(data_types.Array(data_types.Double(), 4), 4),
            "m"),
    })
    return expressions.Identifier(data_types.Pointer32(matrix), "this")


def _element(name):
    return expressions.Identifier(data_types.Double(), name)


def _assignments(names):
    return [
        instructions.Assignment(
            do_pointer_dereference(_this(), index * 8, 8), _element(name))
        for index, name in enumerate(names)
    ]


def _emit(instr):
    writer = Writer(max_line_len=40)
    instr.emit_code(writer)
    return writer.get_string()


class TestMatrixDefinitions(unittest.TestCase):
    def test_collapse(self):
        names = ["e{}".format(i) for i in range(16)]
        block, collapsed = _collapse_block(
            _assignments(names), "m", "DEFINE_MATRIX", 4, 4)
        self.assertTrue(collapsed)
        self.assertEqual(1, len(block))
        self.assertEqual(
            "DEFINE_MATRIX(\n"
            "    e0, e1, e2, e3,\n"
            "    e4, e5, e6, e7,\n"
            "    e8, e9, e10, e11,\n"
            "    e12, e13, e14, e15\n"
            ")\n",
            _emit(block[0]))

    def test_long_row(self):
        names = ["element_{}".format(i) for i in range(16)]
        block, _ = _collapse_block(
            _assignments(names), "m", "DEFINE_MATRIX", 4, 4)
        lines = _emit(block[0]).split("\n")
        self.assertEqual("    element_0,", lines[1])
        self.assertEqual("    element_15", lines[16])
        self.assertEqual(")", lines[17])

    def test_wrong_order(self):
        names = ["e{}".format(i) for i in range(16)]
        assignments = _assignments(names)
        assignments[1], assignments[2] = assignments[2], assignments[1]
        block, collapsed = _collapse_block(
            assignments, "m", "DEFINE_MATRIX", 4, 4)
        self.assertFalse(collapsed)
        self.assertEqual(16, len(block))
