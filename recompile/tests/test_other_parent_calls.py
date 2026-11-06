import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.other_parent_calls import restore_other_parent_calls
from procedure_declaration import ProcedureDeclaration


def _stackvar(offset):
    return expressions.intermediate.Stackvar(offset, 4)


def _const(value):
    return expressions.Constant(data_types.Int32(), value)


class _Analysis:
    def __init__(self):
        self.types = {}

    def set_stackvar_type(self, offset, data_type):
        self.types[offset] = data_type


class TestOtherParentCalls(unittest.TestCase):
    def setUp(self):
        self.array = data_types.ClassType(
            "Array", {0: (data_types.Int32(), "size")})
        self.node = data_types.ClassType("Node", {})
        self.node.add_other_parent(4, self.array)
        self.append = ProcedureDeclaration(
            "Append", CallingConvention.THISCALL, self.array,
            [(data_types.Int32(), "x")], data_types.Int32())

    def _instrs(self, offset):
        this = expressions.Bin(
            Operator.ADD,
            expressions.ReinterpretCast(data_types.AnyInt(4), _stackvar(-12)),
            _const(offset))
        call = expressions.ProcedureCall(
            is_method=True, proc_decl=self.append,
            arguments=[_stackvar(-472), _const(5)])
        return [
            instructions.Assignment(
                _stackvar(-12), expressions.NewExpression(self.node, [])),
            instructions.Assignment(_stackvar(-472), this),
            instructions.CodeInstruction(call),
        ]

    def test_call_of_other_parent(self):
        analysis = _Analysis()
        instrs = restore_other_parent_calls(self._instrs(4), analysis)
        self.assertEqual(2, len(instrs))
        this = instrs[1].expression.arguments[0]
        self.assertIsInstance(this, expressions.ImplicitCast)
        self.assertEqual("STACKVAR(-12, 4)", this.emit_code())
        self.assertIs(self.node, analysis.types[-12].pointee)

    def test_offset_of_no_parent(self):
        instrs = restore_other_parent_calls(self._instrs(8), _Analysis())
        self.assertEqual(3, len(instrs))
