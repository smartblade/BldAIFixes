import unittest

import data_types
import expressions
import patterns.characteristics as characteristics
from patterns.high_level.transform_constant import transform_constant


def _transform(value):
    procedure = characteristics.Procedure({
        "constants": {"10.0": {"name": "kMargin"}, "-1": {"sizeof": "-4"}},
    })
    c = expressions.Constant(data_types.Double(), value)
    return transform_constant(
        c, file_declarations=None, characteristics=procedure, stack_vars={})


class TestNamedFloatConstants(unittest.TestCase):
    def test_named_constant(self):
        self.assertEqual("kMargin", _transform(10.0).emit_code())

    def test_negated_named_constant(self):
        self.assertEqual("-kMargin", _transform(-10.0).emit_code())

    def test_other_constant(self):
        self.assertIsNone(_transform(2.0))
