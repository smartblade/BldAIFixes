import unittest

import data_types
import expressions
import instructions
from patterns.high_level.split_jumped_declarations import (
    split_jumped_declarations)
from tests.builder import call_instr, i32_id, if_instr
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)


def _declaration():
    return instructions.VariableDeclaration(
        i32_id("x"), expressions.Constant(data_types.Int32(), 1))


def _emit(instrs):
    writer = Writer()
    for instr in split_jumped_declarations(_Procedure(instrs)).instructions:
        instr.emit_code(writer)
    return writer.get_string()


class TestSplitJumpedDeclarations(unittest.TestCase):
    def test_jump_past_declaration(self):
        instrs = [
            if_instr(i32_id("a"), [instructions.Goto("l_end")]),
            _declaration(),
            call_instr(name="f", arguments=[i32_id("x")]),
            instructions.LabeledBlock("l_end", [call_instr(name="g")]),
        ]
        self.assertEqual(
            "if (a)\n"
            "{\n"
            "    goto l_end;\n"
            "}\n"
            "int x;\n"
            "x = 1;\n"
            "f(x);\n"
            "l_end:\n"
            "g();\n",
            _emit(instrs))

    def test_jump_into_nested_block(self):
        instrs = [
            if_instr(i32_id("a"), [instructions.Goto("l_inner")]),
            _declaration(),
            if_instr(i32_id("b"), [
                call_instr(name="f"),
                instructions.LabeledBlock("l_inner", [call_instr(name="g")]),
            ]),
        ]
        self.assertIn("int x;\nx = 1;\n", _emit(instrs))

    def test_jump_inside_scope(self):
        instrs = [
            _declaration(),
            instructions.LabeledBlock("l_loop", [
                call_instr(name="f", arguments=[i32_id("x")]),
                if_instr(i32_id("a"), [instructions.Goto("l_loop")]),
            ]),
        ]
        self.assertIn("int x = 1;\n", _emit(instrs))
