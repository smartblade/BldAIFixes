import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.characteristics.return_characteristics import Return
from patterns.high_level.convert_return_value_to_bool import \
    convert_return_value_to_bool
from patterns.high_level.transform_assignment import transform_assignment
from patterns.high_level.transform_returns import transform_returns


class _ProcDecl:
    def __init__(self, return_type, operator=None):
        self.return_type = return_type
        self.operator = operator
        self.is_constructor = False


class _Characteristics:
    def __init__(self, ret=None):
        self.ret = Return(ret or {})


def _double_id(name):
    return expressions.Identifier(data_types.Double(), name)


class TestFloatingPointReturns(unittest.TestCase):
    def test_return_of_st0(self):
        regdef = instructions.TemporaryRegisterDefinition()
        regdef.push_fpu(_double_id("length"))
        instrs = transform_returns(
            None, _ProcDecl(data_types.Double()), _Characteristics(),
            [regdef, instructions.ReturnInstruction(None)])
        self.assertEqual(1, len(instrs))
        self.assertIsInstance(instrs[0], instructions.ReturnInstruction)
        self.assertEqual("length", instrs[0].expression.emit_code())

    def test_return_of_st0_as_float(self):
        regdef = instructions.TemporaryRegisterDefinition()
        regdef.push_fpu(_double_id("length"))
        instrs = transform_returns(
            None, _ProcDecl(data_types.Float()), _Characteristics(),
            [regdef, instructions.ReturnInstruction(None)])
        self.assertEqual("length", instrs[0].expression.emit_code())


class TestIntegerReturnOfComparison(unittest.TestCase):
    def test_comparison_returns_bool(self):
        value = convert_return_value_to_bool(
            _ProcDecl(data_types.Int32(), Operator.EQ), _Characteristics(),
            expressions.Constant(data_types.Int32(), 1))
        self.assertEqual("true", value.emit_code())

    def test_comparison_returns_int(self):
        value = convert_return_value_to_bool(
            _ProcDecl(data_types.Int32(), Operator.EQ),
            _Characteristics({"boolean": "no"}),
            expressions.Constant(data_types.Int32(), 1))
        self.assertEqual("1", value.emit_code())


class TestFloatingPointCompoundAssignment(unittest.TestCase):
    def test_division(self):
        x, y = _double_id("x"), _double_id("y")
        instr = transform_assignment(
            x, expressions.Bin(Operator.DIV, x, y), analysis=None)
        self.assertEqual("x /= y", instr.expression.emit_code())

    def test_destination_on_the_right(self):
        x, y = _double_id("x"), _double_id("y")
        e = transform_assignment(
            x, expressions.Bin(Operator.MUL, y, x), analysis=_NoAnalysis())
        self.assertIsNone(e)


class _NoAnalysis:
    def process_assignment(self, dst, src):
        pass
