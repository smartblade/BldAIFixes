import unittest

from tests.builder import add, and_op, ass, call, call_instr, gt, if_instr
from tests.builder import i32_id, lt, mul, string
from writer import Writer


class TestWriter(unittest.TestCase):
    @staticmethod
    def _write_instruction(instr, max_line_len=80):
        writer = Writer(max_line_len=max_line_len)
        instr.emit_code(writer)
        return "\n" + writer.get_string()

    def test_write_wrapped_if(self):
        a = i32_id("very_long_identifier_a")
        b = i32_id("very_long_identifier_b")
        c = i32_id("very_long_identifier_c")
        instr = if_instr(if_clause=and_op(lt(a, b), gt(b, c)), if_block=[])

        code = self._write_instruction(instr)

        expected = """
if (
    very_long_identifier_a < very_long_identifier_b &&
    very_long_identifier_b > very_long_identifier_c
)
{
}
"""
        self.assertEqual(expected, code)

    def test_write_wrapped_if_and_add_lt(self):
        a = i32_id("very_long_identifier_a")
        b = i32_id("very_long_identifier_b")
        c = i32_id("very_long_identifier_c")
        instr = if_instr(
            if_clause=and_op(call(name="p"), lt(add(a, b), c)),
            if_block=[],
        )

        code = self._write_instruction(instr)

        expected = """
if (
    p() &&
    very_long_identifier_a + very_long_identifier_b < very_long_identifier_c
)
{
}
"""
        self.assertEqual(expected, code)

    def test_write_wrapped_procedure_call(self):
        a = i32_id("very_long_identifier_a")
        b = i32_id("very_long_identifier_b")
        c = i32_id("very_long_identifier_c")
        instr = call_instr(name="proc_abc", arguments=[a, b, c])

        code = self._write_instruction(instr)

        expected = """
proc_abc(
    very_long_identifier_a,
    very_long_identifier_b,
    very_long_identifier_c
);
"""
        self.assertEqual(expected, code)

    def test_write_wrapped_assignment(self):
        a = i32_id("very_long_identifier_a")
        b = i32_id("very_long_identifier_b")
        c = i32_id("very_long_identifier_c")
        d = i32_id("very_long_identifier_d")
        instr = ass(a, add(b, c, d))

        code = self._write_instruction(instr)

        expected = """
very_long_identifier_a =
    very_long_identifier_b + very_long_identifier_c + very_long_identifier_d;
"""
        self.assertEqual(expected, code)

    def test_write_wrapped_nested_calls(self):
        a = i32_id("very_long_identifier_a")
        b = i32_id("very_long_identifier_b")
        c = i32_id("very_long_identifier_c")
        d = i32_id("very_long_identifier_d")
        instr = call_instr(
            name="proc_a",
            arguments=[
                call(
                    name="proc_b",
                    arguments=[a, add(a, b, c, d), add(b, c, d)],
                ),
                call(name="proc_c", arguments=[add(a, b, mul(c, d))]),
            ],
        )

        code = self._write_instruction(instr)

        expected = """
proc_a(
    proc_b(
        very_long_identifier_a,
        very_long_identifier_a +
            very_long_identifier_b +
            very_long_identifier_c +
            very_long_identifier_d,
        very_long_identifier_b + very_long_identifier_c + very_long_identifier_d
    ),
    proc_c(
        very_long_identifier_a +
            very_long_identifier_b +
            very_long_identifier_c * very_long_identifier_d
    )
);
"""
        self.assertEqual(expected, code)

    def test_write_wrapped_string(self):
        instr = call_instr(
            name="proc",
            arguments=[
                string("This is some string to be splitted to several lines"),
            ],
        )

        code = self._write_instruction(instr, max_line_len=30)

        expected = """
proc(
    "This is some string to "
        "be splitted to "
        "several lines"
);
"""
        self.assertEqual(expected, code)
