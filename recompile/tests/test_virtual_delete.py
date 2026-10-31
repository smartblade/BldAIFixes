import unittest

from custom_block_transformer import transform_block
import data_types
import expressions
from expression_transformer import ExpressionTransformer
import instructions
from patterns.high_level.inline_functions.transform_block_instructions import (
    _transform_virtual_delete)
from tests.builder import ass, i32_id, if_instr
from writer import Writer


def _stackvar(offset):
    return expressions.intermediate.Stackvar(offset, 4)


def _const(value):
    return expressions.Constant(data_types.Unknown32(), value)


class _Transformer(ExpressionTransformer):
    @staticmethod
    def transform_block_instructions(block_instructions, stack_vars, **kwargs):
        instr = block_instructions.get_current_instruction()
        if isinstance(instr, instructions.IfInstruction):
            _transform_virtual_delete(block_instructions, instr, stack_vars)


def _deleting_instructions(flag):
    vtbl = expressions.intermediate.Access(_stackvar(-8), 0, 4)
    deleting_call = expressions.ProcedureCall(
        callee=expressions.intermediate.Access(vtbl, 4, 4),
        is_method=True,
        arguments=[_stackvar(-8), _const(flag)],
    )
    return [
        ass(_stackvar(-12), i32_id("obj")),
        ass(_stackvar(-8), _stackvar(-12)),
        if_instr(
            expressions.Bin(
                expressions.operator.Operator.NE, _stackvar(-8), _const(0)),
            [ass(_stackvar(-20), deleting_call)],
            [ass(_stackvar(-20), _const(0))],
        ),
    ]


def _emit(instrs):
    instrs = transform_block(instrs, _Transformer, stack_vars={})
    writer = Writer()
    for instr in instrs:
        instr.emit_code(writer)
    return writer.get_string()


class TestVirtualDelete(unittest.TestCase):
    def test_virtual_delete(self):
        self.assertEqual("delete obj;\n", _emit(_deleting_instructions(1)))

    def test_destructor_without_deleting(self):
        self.assertNotIn("delete", _emit(_deleting_instructions(0)))
