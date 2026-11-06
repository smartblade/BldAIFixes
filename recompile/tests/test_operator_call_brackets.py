import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from procedure_declaration import ProcedureDeclaration


def _vector():
    return data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })


def _operator_call(vector, operator, left, right, right_type):
    proc_decl = ProcedureDeclaration(
        "operator {}".format(operator), CallingConvention.THISCALL, vector,
        [(right_type, "that")], vector)
    return expressions.ProcedureCall(
        is_method=True, proc_decl=proc_decl, arguments=[left, right])


class TestOperatorCallBrackets(unittest.TestCase):
    def setUp(self):
        self.vector = _vector()
        self.a = expressions.Identifier(self.vector, "a")
        self.b = expressions.Identifier(self.vector, "b")
        self.half = expressions.Constant(data_types.Double(), 0.5)

    def test_sum_multiplied(self):
        vector_ref = data_types.Reference(self.vector)
        sum_call = _operator_call(
            self.vector, "+", self.a, self.b, vector_ref)
        call = _operator_call(
            self.vector, "*", sum_call, self.half, data_types.Double())
        self.assertEqual("(a + b) * 0.5", call.emit_code())

    def test_product_added(self):
        vector_ref = data_types.Reference(self.vector)
        product = _operator_call(
            self.vector, "*", self.b, self.half, data_types.Double())
        call = _operator_call(self.vector, "+", self.a, product, vector_ref)
        self.assertEqual("a + b * 0.5", call.emit_code())

    def test_right_difference_subtracted(self):
        vector_ref = data_types.Reference(self.vector)
        difference = _operator_call(
            self.vector, "-", self.a, self.b, vector_ref)
        call = _operator_call(
            self.vector, "-", self.a, difference, vector_ref)
        self.assertEqual("a - (a - b)", call.emit_code())
