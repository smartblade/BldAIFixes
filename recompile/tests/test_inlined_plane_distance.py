import json
import os
import unittest

from patterns.asm_parser import parse_asm_lines
from patterns.asm_patterns import _match_instructions_pattern
from patterns.structure import Patterns

# Inlined B_Plane::Distance(&sphere->center) at 0x004532F6 of Blade.exe
_distance_asm = """
mov eax, dword ptr [ebp-018h]
mov ecx, dword ptr [ebp-018h]
mov edx, dword ptr [ebp+00Ch]
fld qword ptr [edx+010h]
fmul qword ptr [ecx+014h]
mov ecx, dword ptr [ebp-018h]
mov edx, dword ptr [ebp+00Ch]
fld qword ptr [edx+008h]
fmul qword ptr [ecx+00Ch]
mov ecx, dword ptr [ebp-018h]
mov edx, dword ptr [ebp+00Ch]
fld qword ptr [edx]
fmul qword ptr [ecx+004h]
faddp st(01h), st(00h)
faddp st(01h), st(00h)
fadd qword ptr [eax+01Ch]
"""


def _load_patterns():
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "patterns", "patterns.json")
    with open(file_path) as f:
        return Patterns(json.load(f))


def _find_pattern(patterns, action_name):
    for pattern in patterns._instructions_patterns:
        action = pattern.action
        if action is not None and action.name == action_name:
            return pattern
    return None


class TestInlinedPlaneDistance(unittest.TestCase):
    def setUp(self):
        self.patterns = _load_patterns()
        self.pattern = _find_pattern(self.patterns, "fpu-method-call")

    def _match(self, asm):
        instrs = parse_asm_lines(
            asm.strip().split("\n"), self.patterns.commands_code_dict)
        return _match_instructions_pattern(self.pattern, 0, instrs), instrs

    def test_inlined_distance(self):
        (last_index, match_dict), instrs = self._match(_distance_asm)
        self.assertEqual(len(instrs), last_index)

    def test_other_dot_product_is_not_matched(self):
        # Product of other fields is not the distance to the plane
        asm = _distance_asm.replace("[eax+01Ch]", "[eax+024h]")
        (last_index, match_dict), instrs = self._match(asm)
        self.assertEqual(-1, last_index)
