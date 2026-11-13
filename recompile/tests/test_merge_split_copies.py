import unittest

import data_types
import expressions
from patterns.high_level.merge_split_copies import merge_split_copies
from tests.builder import ass, call_instr
from writer import Writer


def _stackvar(offset, size=4):
    return expressions.intermediate.Stackvar(offset, size)


def _emit(instrs, double_offsets=()):
    writer = Writer()
    for instr in merge_split_copies(instrs, double_offsets):
        instr.emit_code(writer)
    return writer.get_string()


class TestMergeSplitCopies(unittest.TestCase):
    def test_copy_of_double(self):
        instrs = [
            call_instr(name="f", arguments=[_stackvar(-16, 8)]),
            ass(_stackvar(-232), _stackvar(-16)),
            ass(_stackvar(-228), _stackvar(-12)),
        ]
        self.assertEqual(
            "f(STACKVAR(-16, 8));\nSTACKVAR(-232, 8) = STACKVAR(-16, 8);\n",
            _emit(instrs))

    def test_copy_to_double(self):
        instrs = [
            ass(_stackvar(-512), _stackvar(-20)),
            ass(_stackvar(-508), _stackvar(-16)),
            call_instr(name="f", arguments=[_stackvar(-512, 8)]),
        ]
        self.assertEqual(
            "STACKVAR(-512, 8) = STACKVAR(-20, 8);\nf(STACKVAR(-512, 8));\n",
            _emit(instrs))

    def test_copy_of_double_field_through_temporary(self):
        # x of a local vector at -36 is copied to a temporary at -520 and
        # then to x of a temporary vector at -196
        instrs = [
            ass(_stackvar(-520), _stackvar(-36)),
            ass(_stackvar(-516), _stackvar(-32)),
            ass(_stackvar(-196), _stackvar(-520)),
            ass(_stackvar(-192), _stackvar(-516)),
        ]
        writer = Writer()
        for instr in merge_split_copies(instrs, {-36}):
            instr.emit_code(writer)
        self.assertEqual(
            "STACKVAR(-520, 8) = STACKVAR(-36, 8);\n"
            "STACKVAR(-196, 8) = STACKVAR(-520, 8);\n",
            writer.get_string())

    def test_copies_of_ints(self):
        instrs = [
            ass(_stackvar(-232), _stackvar(-16)),
            ass(_stackvar(-228), _stackvar(-12)),
        ]
        self.assertEqual(
            "STACKVAR(-232, 4) = STACKVAR(-16, 4);\n"
            "STACKVAR(-228, 4) = STACKVAR(-12, 4);\n",
            _emit(instrs))

    def test_overlapping_copy(self):
        instrs = [
            call_instr(name="f", arguments=[_stackvar(-16, 8)]),
            ass(_stackvar(-12), _stackvar(-16)),
            ass(_stackvar(-8), _stackvar(-12)),
        ]
        self.assertIn("STACKVAR(-12, 4) = STACKVAR(-16, 4);\n", _emit(instrs))

    def test_zero_of_double(self):
        # x(0.0) of an inlined 'B_Vector()'
        zero = expressions.Constant(data_types.Int32(), 0)
        instrs = [ass(_stackvar(-24), zero), ass(_stackvar(-20), zero)]
        self.assertEqual(
            "STACKVAR(-24, 8) = 0.0;\n", _emit(instrs, double_offsets={-24}))

    def test_zeros_of_other_halves(self):
        zero = expressions.Constant(data_types.Int32(), 0)
        instrs = [ass(_stackvar(-24), zero), ass(_stackvar(-20), zero)]
        self.assertEqual(
            "STACKVAR(-24, 4) = 0;\nSTACKVAR(-20, 4) = 0;\n", _emit(instrs))
