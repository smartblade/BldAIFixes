import unittest

import data_types
import expressions
from patterns.high_level.transform_reinterpret import \
    _transform_to_first_field


def _vector():
    return data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })


def _box_pointer():
    box = data_types.ClassType("B_BoundingBox", {
        0: (_vector(), "minCoords"),
        24: (_vector(), "maxCoords"),
    })
    return expressions.Identifier(data_types.Pointer32(box), "box")


class TestFirstFieldCast(unittest.TestCase):
    def test_cast_to_first_field(self):
        e = _transform_to_first_field(
            data_types.Pointer32(_vector()), _box_pointer())
        self.assertEqual("&box->minCoords", e.emit_code())

    def test_cast_to_other_type(self):
        self.assertIsNone(_transform_to_first_field(
            data_types.Pointer32(data_types.Int32()), _box_pointer()))
