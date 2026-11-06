import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.new_expressions import fold_new_expressions
from procedure_declaration import ProcedureDeclaration


def _stackvar(offset):
    return expressions.intermediate.Stackvar(offset, 4)


def _node():
    node = data_types.ClassType("Node", {4: (data_types.Int32(), "value")})
    node.add_constructor(ProcedureDeclaration(
        "Node", CallingConvention.THISCALL, node,
        [(data_types.Int32(), "value")], None))
    return node


def _operator_new(size):
    return expressions.ProcedureCall(
        name="operator new",
        arguments=[expressions.Constant(data_types.UInt32(), size)])


def _construction(node, temporary, dst, arguments):
    ctor = node.constructors[0]
    call = expressions.ProcedureCall(
        is_method=True, proc_decl=ctor,
        arguments=[expressions.ReinterpretCast(
            data_types.Pointer32(node), temporary)] + arguments)
    check = expressions.Bin(
        Operator.NE, temporary, expressions.Constant(data_types.Int32(), 0))
    return instructions.Assignment(dst, expressions.ConditionalOperator(
        check, call, expressions.Constant(data_types.Int32(), 0)))


class TestNewExpressions(unittest.TestCase):
    def setUp(self):
        self.node = _node()
        self.value = expressions.Constant(data_types.Int32(), 5)

    def test_new_expression(self):
        instrs = [
            instructions.Assignment(_stackvar(-8), _operator_new(8)),
            _construction(self.node, _stackvar(-8), _stackvar(-4), [
                self.value]),
        ]
        result = fold_new_expressions(instrs)
        self.assertEqual(1, len(result))
        self.assertEqual("new Node(5)", result[0].src.emit_code())
        self.assertEqual(
            "STACKVAR(-4, 4)", result[0].dst.emit_code())

    def test_temporary_used_later(self):
        instrs = [
            instructions.Assignment(_stackvar(-8), _operator_new(8)),
            _construction(self.node, _stackvar(-8), _stackvar(-4), [
                self.value]),
            instructions.Assignment(_stackvar(-12), _stackvar(-8)),
        ]
        self.assertEqual(3, len(fold_new_expressions(instrs)))

    def test_construction_in_other_variable(self):
        instrs = [
            instructions.Assignment(_stackvar(-8), _operator_new(8)),
            _construction(self.node, _stackvar(-16), _stackvar(-4), [
                self.value]),
        ]
        self.assertEqual(2, len(fold_new_expressions(instrs)))
