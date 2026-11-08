import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from custom_block_transformer import transform_block
from patterns.high_level.conditional_results import fold_conditional_results
from patterns.high_level.operands_order import order_operands
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)

    def transform(self, transformer, **kwargs):
        return _Procedure(
            transform_block(self.instructions, transformer, **kwargs))


def _double(name):
    return expressions.Identifier(data_types.Double(), name)


def _emit(procedure):
    writer = Writer()
    for instr in procedure.instructions:
        instr.emit_code(writer)
    return writer.get_string()


class TestOperandsOrder(unittest.TestCase):
    def setUp(self):
        self.max_x = _double("max_x")
        self.size = _double("size")
        self.stack_vars = {-16: self.max_x}
        # Computed value of an element: x * 2.0
        self.x = expressions.Bin(
            Operator.MUL, _double("x"),
            expressions.Constant(data_types.Double(), 2.0))

    def _order(self, clause):
        result = order_operands(
            _Procedure([instructions.CodeInstruction(clause)]),
            self.stack_vars)
        return _emit(result)

    def test_local_variable_first(self):
        self.assertEqual(
            "max_x > x * 2.0;\n",
            self._order(expressions.Bin(Operator.LT, self.x, self.max_x)))

    def test_parameter_stays_right(self):
        self.assertEqual(
            "x * 2.0 < size;\n",
            self._order(expressions.Bin(Operator.LT, self.x, self.size)))

    def test_conditional_result_first(self):
        conditional = expressions.ConditionalOperator(
            expressions.Bin(Operator.GT, self.max_x, self.size),
            self.max_x, self.size)
        clause = expressions.Bin(Operator.ADD, self.x, conditional)
        self.assertEqual("max(max_x, size) + x * 2.0;\n", self._order(clause))


class TestConditionalResults(unittest.TestCase):
    def test_typed_temporary(self):
        t = _double("unknown_loc_13C")
        a, b, m = _double("a"), _double("b"), _double("m")
        instrs = [
            instructions.IfInstruction(
                expressions.Bin(Operator.GT, a, b),
                [instructions.Assignment(t, a)],
                [instructions.Assignment(t, b)]),
            instructions.Assignment(m, t),
        ]
        self.assertEqual(
            "m = max(a, b);\n", _emit(fold_conditional_results(
                _Procedure(instrs))))

    def test_named_variable(self):
        t = _double("result")
        a, b, m = _double("a"), _double("b"), _double("m")
        instrs = [
            instructions.IfInstruction(
                expressions.Bin(Operator.GT, a, b),
                [instructions.Assignment(t, a)],
                [instructions.Assignment(t, b)]),
            instructions.Assignment(m, t),
        ]
        result = fold_conditional_results(_Procedure(instrs))
        self.assertEqual(2, len(result.instructions))
