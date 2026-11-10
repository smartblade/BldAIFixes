import unittest

import data_types
import expressions
from expressions.operator import Operator
from patterns.high_level.transform_arrptr import transform_arrptr
from tests.builder import i32_id


def _node_pointer():
    node = data_types.ClassType("B_Node", {
        0: (data_types.Int32(), "count"),
        4: (data_types.Array(data_types.Pointer32(data_types.Int32()), 8),
            "children"),
    })
    return expressions.Identifier(data_types.Pointer32(node), "node")


class TestTransformArrptr(unittest.TestCase):
    def test_element_of_array_field(self):
        e = transform_arrptr(_node_pointer(), 4, i32_id("i"), 4)
        self.assertEqual("&node->children[i]", e.emit_code())

    def test_element_size_mismatch(self):
        self.assertIsNone(transform_arrptr(_node_pointer(), 8, i32_id("i"), 4))

    def test_not_array_field(self):
        self.assertIsNone(transform_arrptr(_node_pointer(), 4, i32_id("i"), 0))

    def test_field_of_element_with_scaled_index(self):
        item = data_types.ClassType("B_Item", {
            0: (data_types.Int32(), "a"),
            4: (data_types.Int32(), "b"),
        })
        cache = data_types.ClassType("B_Cache", {
            0: (data_types.Int32(), "count"),
            4: (data_types.Array(item, 16), "items"),
        })
        base = expressions.Identifier(data_types.Pointer32(cache), "cache")
        index = expressions.Bin(
            Operator.MUL, expressions.Constant(data_types.Int32(), 8),
            i32_id("i"))
        e = transform_arrptr(base, 1, index, 8)
        self.assertEqual("&cache->items[i].b", e.emit_code())

    def test_element_pointed_by_pointer(self):
        base = expressions.Identifier(
            data_types.Pointer32(data_types.Pointer32(data_types.Int32())),
            "elements")
        e = transform_arrptr(base, 4, i32_id("i"), 0)
        self.assertEqual("&elements[i]", e.emit_code())
        self.assertIsNone(transform_arrptr(base, 8, i32_id("i"), 0))

    def test_element_of_row_of_matrix(self):
        matrix = data_types.ClassType("B_Matrix", {
            0: (data_types.Array(
                data_types.Array(data_types.Double(), 4), 4), "m"),
        })
        out = expressions.Identifier(data_types.Reference(matrix), "out")
        this = expressions.Identifier(data_types.Pointer32(matrix), "this")
        # 'reinterpret_cast<int>(out) + 32 * i' is the address of out.m[i]
        row = expressions.Bin(
            Operator.ADD,
            expressions.ReinterpretCast(data_types.Int32(), out),
            expressions.Bin(
                Operator.MUL, expressions.Constant(data_types.Int32(), 32),
                i32_id("i")))
        e = transform_arrptr(row, 8, i32_id("j"), 0)
        self.assertEqual("&out.m[i][j]", e.emit_code())
        row = transform_arrptr(this, 32, i32_id("j"), 0)
        self.assertEqual("&this->m[j]", row.emit_code())
        e = transform_arrptr(row, 8, i32_id("i"), 0)
        self.assertEqual("&this->m[j][i]", e.emit_code())
