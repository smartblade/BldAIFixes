import unittest

import data_types
import expressions
from custom_block_transformer import transform_block
from patterns.high_level.variables_declarations import insert_declarations
from tests.builder import ass, call_instr, i32_id, if_instr
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def exclude_implicit_stack_variables(self, stack_vars):
        return stack_vars

    def transform(self, transformer, **kwargs):
        return _Procedure(
            transform_block(self.instructions, transformer, **kwargs))


def _const(value):
    return expressions.Constant(data_types.Int32(), value)


def _emit(instrs, stack_vars):
    writer = Writer()
    procedure = insert_declarations(_Procedure(instrs), stack_vars)
    for instr in procedure.instructions:
        instr.emit_code(writer)
    return writer.get_string()


class TestHoistDeclarations(unittest.TestCase):
    def _instrs(self):
        self.i = i32_id("i")
        self.distance = i32_id("distance")
        return [
            ass(self.i, _const(0)),
            if_instr(self.i, [
                ass(self.distance, _const(1)),
                call_instr(name="f", arguments=[self.distance]),
            ]),
            call_instr(name="f", arguments=[self.i]),
        ]

    def test_variable_above_variable_of_body(self):
        instrs = self._instrs()
        self.assertEqual(
            "int distance;\n"
            "int i = 0;\n"
            "if (i)\n"
            "{\n"
            "    distance = 1;\n"
            "    f(distance);\n"
            "}\n"
            "f(i);\n",
            _emit(instrs, {-8: self.distance, -12: self.i}))

    def test_variable_below_variables_of_body(self):
        instrs = self._instrs()
        self.assertEqual(
            "int i = 0;\n"
            "if (i)\n"
            "{\n"
            "    int distance = 1;\n"
            "    f(distance);\n"
            "}\n"
            "f(i);\n",
            _emit(instrs, {-4: self.i, -8: self.distance}))

    def test_variable_above_variable_of_preceding_block(self):
        x, y = i32_id("x"), i32_id("y")
        instrs = [
            if_instr(i32_id("a"), [
                ass(x, _const(1)),
                call_instr(name="f", arguments=[x]),
            ]),
            if_instr(i32_id("b"), [
                ass(y, _const(2)),
                call_instr(name="f", arguments=[y]),
            ]),
        ]
        self.assertEqual(
            "int y;\n"
            "if (a)\n"
            "{\n"
            "    int x = 1;\n"
            "    f(x);\n"
            "}\n"
            "if (b)\n"
            "{\n"
            "    y = 2;\n"
            "    f(y);\n"
            "}\n",
            _emit(instrs, {-4: y, -8: x}))


class TestDeclarationsInBuckets(unittest.TestCase):
    def test_lower_variable_of_bucket_declared_first(self):
        # outBuffer and boxCenter are in bucket 0: boxCenter above outBuffer
        # is declared later
        out_buffer = i32_id("outBuffer")
        box_center = i32_id("boxCenter")
        instrs = [
            ass(box_center, _const(1)),
            call_instr(name="f", arguments=[box_center]),
            ass(out_buffer, _const(2)),
            call_instr(name="f", arguments=[out_buffer]),
        ]
        self.assertEqual(
            "int outBuffer;\n"
            "int boxCenter = 1;\n"
            "f(boxCenter);\n"
            "outBuffer = 2;\n"
            "f(outBuffer);\n",
            _emit(instrs, {-36: box_center, -60: out_buffer}))

    def test_variables_of_other_buckets(self):
        # i (bucket 9) and boxCenter (bucket 0) are placed by buckets
        i = i32_id("i")
        box_center = i32_id("boxCenter")
        instrs = [
            ass(box_center, _const(1)),
            call_instr(name="f", arguments=[box_center]),
            ass(i, _const(2)),
            call_instr(name="f", arguments=[i]),
        ]
        self.assertIn("int i = 2;\n", _emit(instrs, {-36: box_center, -60: i}))
