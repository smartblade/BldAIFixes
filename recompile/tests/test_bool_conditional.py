import unittest

import data_types
import expressions
from expressions.operator import Operator
from patterns.high_level.transform_binary import _transform_bool_conditional
from tests.builder import i32_id


def _conditional(then_value, else_value):
    condition = expressions.Bin(Operator.GT, i32_id("x"), i32_id("y"))
    return expressions.ConditionalOperator(
        condition,
        expressions.Constant(data_types.Int32(), then_value),
        expressions.Constant(data_types.Int32(), else_value),
    )


def _zero():
    return expressions.Constant(data_types.Int32(), 0)


class TestBoolConditional(unittest.TestCase):
    def test_negated_condition(self):
        e = _transform_bool_conditional(
            Operator.NE, _conditional(0, 1), _zero())
        self.assertEqual("!(x > y)", e.emit_code())

    def test_condition(self):
        e = _transform_bool_conditional(
            Operator.NE, _conditional(1, 0), _zero())
        self.assertEqual("x > y", e.emit_code())
        e = _transform_bool_conditional(
            Operator.EQ, _conditional(0, 1), _zero())
        self.assertEqual("x > y", e.emit_code())

    def test_not_bool_values(self):
        self.assertIsNone(_transform_bool_conditional(
            Operator.NE, _conditional(2, 0), _zero()))
