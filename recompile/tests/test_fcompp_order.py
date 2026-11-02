import json
import os
import unittest

from patterns.asm_parser import parse_asm_lines
from patterns.asm_patterns import _match_instructions_pattern
from patterns.structure import Patterns


def _load_patterns():
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "patterns", "patterns.json")
    with open(file_path) as f:
        return Patterns(json.load(f))


class TestFcomppOrder(unittest.TestCase):
    def test_comparison_with_jump_is_one_pattern(self):
        # Left operand of the source is loaded first, it is st(1)
        patterns = _load_patterns()
        asm = [
            "fcompp",
            "fnstsw ax",
            "test ah, 041h",
            "jne l00453114",
        ]
        for jump in ("je", "jne"):
            asm[-1] = "{} l00453114".format(jump)
            instrs = parse_asm_lines(asm, patterns.commands_code_dict)
            matched = [
                pattern for pattern in patterns._instructions_patterns
                if _match_instructions_pattern(pattern, 0, instrs)[0] == 4
            ]
            self.assertEqual(1, len(matched))
            condition = matched[0].actions[2].arguments["condition"]
            operator = condition._expression.operator.value
            self.assertEqual(">=" if jump == "jne" else "<", operator)
