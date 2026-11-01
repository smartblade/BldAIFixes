import unittest

import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.procedure import _is_scalar_deleting_destructor


class _ProcInfo:
    def __init__(self, this):
        self._this = this

    def is_this_expression(self, e):
        return e is self._this


def _destructor(this, deleted):
    flags = expressions.Identifier(data_types.Int32(), "flags")
    regdef = instructions.TemporaryRegisterDefinition()
    regdef.define_reg_value("eax", this)
    return [
        instructions.IfInstruction(
            expressions.Bin(Operator.BIT_AND, flags, expressions.Constant(
                data_types.Int32(), 1)),
            [instructions.CodeInstruction(expressions.ProcedureCall(
                name="operator delete", arguments=[deleted]))]),
        regdef,
    ]


class TestScalarDeletingDestructor(unittest.TestCase):
    def test_scalar_deleting_destructor(self):
        this = expressions.Identifier(data_types.Pointer32(), "this")
        self.assertTrue(_is_scalar_deleting_destructor(
            _ProcInfo(this), _destructor(this, this)))

    def test_deletion_of_other_object(self):
        this = expressions.Identifier(data_types.Pointer32(), "this")
        other = expressions.Identifier(data_types.Pointer32(), "other")
        self.assertFalse(_is_scalar_deleting_destructor(
            _ProcInfo(this), _destructor(this, other)))
