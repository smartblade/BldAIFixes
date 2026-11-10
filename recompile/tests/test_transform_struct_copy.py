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

    def test_copy_to_object_pointed_by_pointer(self):
        vector, box = _types()
        out = expressions.Identifier(data_types.Pointer32(box), "out")
        temp = expressions.Identifier(box, "temp")
        instr = transform_struct_copy(
            _memcpy(out, expressions.AddressOf(temp), 48))
        self.assertEqual("*out = temp;\n", _emit(instr))

    def test_copy_to_returned_object(self):
        vector, box = _types()
        result = expressions.Identifier(
            data_types.Pointer32(box), "__result")
        temp = expressions.Identifier(box, "temp")
        self.assertIsNone(transform_struct_copy(
            _memcpy(result, expressions.AddressOf(temp), 48)))
