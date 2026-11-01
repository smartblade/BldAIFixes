import unittest

import data_types
import expressions
from expressions.operator import Operator
from patterns.high_level.transform_binary import \
    _transform_field_element_offset
from tests.builder import i32_id


class TestFieldElementOffset(unittest.TestCase):
    def test_address_of_element_of_array_field(self):
        item = data_types.ClassType("B_Item", {
            0: (data_types.Int32(), "a"),
            4: (data_types.Int32(), "b"),
        })
        cache = data_types.ClassType("B_Cache", {
            0: (data_types.Int32(), "count"),
            4: (data_types.Array(item, 16), "items"),
        })
        ptr = expressions.Identifier(data_types.Pointer32(cache), "cache")
        index = expressions.Bin(
            Operator.MUL, expressions.Constant(data_types.Int32(), 8),
            i32_id("i"))
        e = _transform_field_element_offset(
            expressions.ReinterpretCast(data_types.AnyInt32(), ptr), index,
            expressions.Constant(data_types.Int32(), 4))
        self.assertEqual("&cache->items[i]", e.emit_code())
