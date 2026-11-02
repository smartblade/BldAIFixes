import json
import os
import unittest

import data_types
import expressions
from patterns.asm_parser import parse_asm_lines
from patterns.asm_patterns import _match_instructions_pattern
from patterns.structure import Patterns

# Inlined B_PtrArray<B_Sector>::Append at 0x0045021D of Blade.exe
_append_asm = """
mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [ebp+00Ch]
mov edx, dword ptr [eax+010h]
cmp edx, dword ptr [ecx+008h]
jbe l00450252
mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [eax+008h]
mov edx, dword ptr [ebp+00Ch]
mov eax, dword ptr [edx+004h]
mov edx, dword ptr [ebp-00Ch]
mov dword ptr [eax+ecx*04h], edx
mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [eax+008h]
add ecx, 000000001h
mov edx, dword ptr [ebp+00Ch]
mov dword ptr [edx+008h], ecx
jmp near ptr l0045031B
l00450252: mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [eax+010h]
mov edx, dword ptr [ebp+00Ch]
add ecx, dword ptr [edx+00Ch]
mov eax, dword ptr [ebp+00Ch]
mov dword ptr [eax+010h], ecx
mov ecx, dword ptr [ebp+00Ch]
cmp dword ptr [ecx+008h], 000000000h
je l004502DC
mov edx, dword ptr [ebp+00Ch]
mov eax, dword ptr [edx+010h]
shl eax, 002h
push eax
call l005BBD38; [SHW32.shi_new].
add esp, 000000004h
mov dword ptr [ebp-018h], eax
mov ecx, dword ptr [ebp-018h]
mov dword ptr [ebp-010h], ecx
mov dword ptr [ebp-014h], 000000000h
jmp l0045029A
l00450291: mov edx, dword ptr [ebp-014h]
add edx, 000000001h
mov dword ptr [ebp-014h], edx
l0045029A: mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [ebp-014h]
cmp ecx, dword ptr [eax+008h]
jnb l004502BC
mov edx, dword ptr [ebp+00Ch]
mov eax, dword ptr [edx+004h]
mov ecx, dword ptr [ebp-014h]
mov edx, dword ptr [ebp-010h]
mov esi, dword ptr [ebp-014h]
mov eax, dword ptr [eax+esi*04h]
mov dword ptr [edx+ecx*04h], eax
jmp l00450291
l004502BC: mov ecx, dword ptr [ebp+00Ch]
mov edx, dword ptr [ecx+004h]
mov dword ptr [ebp-01Ch], edx
mov eax, dword ptr [ebp-01Ch]
push eax
call l005BBD3D; [SHW32.shi_delete].
add esp, 000000004h
mov ecx, dword ptr [ebp+00Ch]
mov edx, dword ptr [ebp-010h]
mov dword ptr [ecx+004h], edx
jmp l004502FA
l004502DC: mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [eax+010h]
shl ecx, 002h
push ecx
call l005BBD38; [SHW32.shi_new].
add esp, 000000004h
mov dword ptr [ebp-020h], eax
mov edx, dword ptr [ebp+00Ch]
mov eax, dword ptr [ebp-020h]
mov dword ptr [edx+004h], eax
l004502FA: mov ecx, dword ptr [ebp+00Ch]
mov edx, dword ptr [ecx+008h]
mov eax, dword ptr [ebp+00Ch]
mov ecx, dword ptr [eax+004h]
mov eax, dword ptr [ebp-00Ch]
mov dword ptr [ecx+edx*04h], eax
mov ecx, dword ptr [ebp+00Ch]
mov edx, dword ptr [ecx+008h]
add edx, 000000001h
mov eax, dword ptr [ebp+00Ch]
mov dword ptr [eax+008h], edx
"""


def _load_patterns():
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "patterns", "patterns.json")
    with open(file_path) as f:
        return Patterns(json.load(f))


def _find_append_pattern(patterns):
    for pattern in patterns._instructions_patterns:
        action = pattern.action
        if action is not None and action.name == "method-call":
            return pattern
    return None


class TestInlinedAppend(unittest.TestCase):
    def setUp(self):
        self.patterns = _load_patterns()
        self.pattern = _find_append_pattern(self.patterns)

    def _match(self, asm):
        instrs = parse_asm_lines(
            asm.strip().split("\n"), self.patterns.commands_code_dict)
        return _match_instructions_pattern(self.pattern, 0, instrs), instrs

    def test_inlined_append(self):
        (last_index, match_dict), instrs = self._match(_append_asm)
        self.assertEqual(len(instrs), last_index)

    def test_append_procedure_is_not_matched(self):
        # Argument of not inlined Append is the parameter at [ebp+008h]
        asm = _append_asm.replace("[ebp-00Ch]", "[ebp+008h]")
        (last_index, match_dict), instrs = self._match(asm)
        self.assertEqual(-1, last_index)

    def test_method_call_of_reference(self):
        vector = data_types.ClassType("B_Array", {})
        array = expressions.Identifier(data_types.Reference(vector), "array")
        pc = expressions.ProcedureCall(
            name="Append", is_method=True,
            arguments=[array, expressions.Identifier(None, "item")])
        self.assertEqual("array.Append(item)", pc.emit_code())
