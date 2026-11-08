import unittest

import data_types
from patterns.high_level.transform_global import transform_global


class _Variable:
    def __init__(self, declaration):
        self.declaration = declaration


class _Symbols:
    def __init__(self, variables):
        self.variables = variables


class _Declarations:
    def __init__(self, variables, declared_types):
        self.symbols = _Symbols(variables)
        self.declared_types = declared_types


class TestGlobalFields(unittest.TestCase):
    def setUp(self):
        array = data_types.ClassType("Array", {
            4: (data_types.Pointer32(data_types.Int32()), "elements"),
            8: (data_types.UInt32(), "size"),
        })
        points = data_types.ClassType("Points", {0: (array, "points")})
        self.declarations = _Declarations(
            {0x005DF898: _Variable("extern Points gbl_points;")},
            {"Points": points, "Array": array})

    def test_object(self):
        self.assertEqual(
            "&gbl_points",
            transform_global(0x005DF898, self.declarations).emit_code())

    def test_field_of_object(self):
        self.assertEqual(
            "&gbl_points.points.size",
            transform_global(0x005DF8A0, self.declarations).emit_code())

    def test_address_after_object(self):
        self.assertIsNone(transform_global(0x005DF8A4, self.declarations))
