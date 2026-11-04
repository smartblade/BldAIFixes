import json
import os
import unittest

from patterns.asm_parser import parse_asm_lines
from patterns.asm_patterns import _match_instructions_pattern
from patterns.structure import Patterns

# Inlined B_PtrArray<B_Sector>::Clear(false) at 0x0045052A of Blade.exe
_clear_asm = """
mov eax, dword ptr [ebp-014h]
cmp dword ptr [eax+010h], 000000000h
jne l0045053E
jmp near ptr l004505C9
l0045053E: xor ecx, ecx
test ecx, ecx
je l00450596
mov dword ptr [ebp-004h], 000000000h
jmp l00450556
l0045054D: mov edx, dword ptr [ebp-004h]
add edx, 000000001h
mov dword ptr [ebp-004h], edx
l00450556: mov eax, dword ptr [ebp-014h]
mov ecx, dword ptr [ebp-004h]
cmp ecx, dword ptr [eax+008h]
jnb l00450596
mov edx, dword ptr [ebp-014h]
mov eax, dword ptr [edx+004h]
mov ecx, dword ptr [ebp-004h]
mov edx, dword ptr [eax+ecx*04h]
mov dword ptr [ebp-00Ch], edx
mov eax, dword ptr [ebp-00Ch]
mov dword ptr [ebp-008h], eax
cmp dword ptr [ebp-008h], 000000000h
je l0045058D
push 000000001h
mov ecx, dword ptr [ebp-008h]
mov edx, dword ptr [ecx]
mov ecx, dword ptr [ebp-008h]
call [edx]
mov dword ptr [ebp-034h], eax
jmp l00450594
l0045058D: mov dword ptr [ebp-034h], 000000000h
l00450594: jmp l0045054D
l00450596: mov eax, dword ptr [ebp-014h]
mov ecx, dword ptr [eax+004h]
mov dword ptr [ebp-010h], ecx
mov edx, dword ptr [ebp-010h]
push edx
call l005BBD3D; [SHW32.shi_delete].
add esp, 000000004h
mov eax, dword ptr [ebp-014h]
mov dword ptr [eax+004h], 000000000h
mov ecx, dword ptr [ebp-014h]
mov dword ptr [ecx+008h], 000000000h
mov edx, dword ptr [ebp-014h]
mov dword ptr [edx+010h], 000000000h
"""


def _load_patterns():
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "patterns", "patterns.json")
    with open(file_path) as f:
        return Patterns(json.load(f))


def _find_method_call_pattern(patterns, name):
    for pattern in patterns._instructions_patterns:
        action = pattern.action
        if (
            action is not None and action.name == "method-call" and
            action.arguments["name"]._expression.emit_code() == name
        ):
            return pattern
    return None


class TestInlinedClear(unittest.TestCase):
    def setUp(self):
        self.patterns = _load_patterns()
        self.pattern = _find_method_call_pattern(self.patterns, "Clear")

    def _match(self, asm):
        instrs = parse_asm_lines(
            asm.strip().split("\n"), self.patterns.commands_code_dict)
        return _match_instructions_pattern(self.pattern, 0, instrs), instrs

    def test_inlined_clear_without_deletion(self):
        (last_index, match_dict), instrs = self._match(_clear_asm)
        self.assertEqual(len(instrs), last_index)

    def test_clear_with_deletion_is_not_matched(self):
        # Clear(true) doesn't skip deletion of items
        asm = _clear_asm.replace("xor ecx, ecx", "mov ecx, 000000001h")
        (last_index, match_dict), instrs = self._match(asm)
        self.assertEqual(-1, last_index)
