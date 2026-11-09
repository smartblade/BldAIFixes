import unittest

import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference


def _node_pointer():
    node = data_types.ClassType("B_Node", {
        0: (data_types.Int32(), "count"),
        4: (data_types.Array(data_types.Pointer32(data_types.Int32()), 8),
            "children"),
    })
    return expressions.Identifier(data_types.Pointer32(node), "node")


def _matrix_pointer():
    matrix = data_types.ClassType("B_Matrix", {
        0: (data_types.Array(data_types.Array(data_types.Double(), 4), 4),
            "m"),
    })
    return expressions.Identifier(data_types.Pointer32(matrix), "this")


class TestDoPointerDereference(unittest.TestCase):
    def test_first_element_of_array_of_arrays(self):
        e = do_pointer_dereference(_matrix_pointer(), 0, 8)
        self.assertEqual("this->m[0][0]", e.emit_code())

    def test_element_of_first_array_of_arrays(self):
        e = do_pointer_dereference(_matrix_pointer(), 8, 8)
        self.assertEqual("this->m[0][1]", e.emit_code())

    def test_element_of_array_of_arrays(self):
        e = do_pointer_dereference(_matrix_pointer(), 0x68, 8)
        self.assertEqual("this->m[3][1]", e.emit_code())

    def test_first_element_of_array_field(self):
        e = do_pointer_dereference(_node_pointer(), 4, 4)
        self.assertEqual("node->children[0]", e.emit_code())

    def test_element_of_array_field(self):
        e = do_pointer_dereference(_node_pointer(), 12, 4)
        self.assertEqual("node->children[2]", e.emit_code())

    def test_several_elements_of_array_field(self):
        self.assertIsNone(do_pointer_dereference(_node_pointer(), 12, 8))
