import unittest

import data_types
import expressions
from patterns.high_level.transform_struct_copy import transform_struct_copy
from writer import Writer


def _types():
    vector = data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })
    box = data_types.ClassType("B_BoundingBox", {
        0: (vector, "minCoords"),
        24: (vector, "maxCoords"),
    })
    return vector, box


def _memcpy(dst, src, size):
    return expressions.ProcedureCall(
        name="memcpy",
        arguments=[dst, src, expressions.Constant(data_types.SizeT(), size)])


def _emit(instr):
    writer = Writer()
    instr.emit_code(writer)
    return writer.get_string()


class TestTransformStructCopy(unittest.TestCase):
    def test_copy_to_field(self):
        vector, box = _types()
        this = expressions.Identifier(data_types.Pointer32(box), "this")
        coords = expressions.Identifier(
            data_types.Reference(vector), "minCoords")
        instr = transform_struct_copy(
            _memcpy(this, expressions.AddressOf(coords), 24))
        self.assertEqual("this->minCoords = minCoords;\n", _emit(instr))

    def test_copy_of_whole_object_to_this(self):
        vector, box = _types()
        this = expressions.Identifier(data_types.Pointer32(box), "this")
        other = expressions.Identifier(data_types.Reference(box), "other")
        self.assertIsNone(transform_struct_copy(
            _memcpy(this, expressions.AddressOf(other), 48)))
