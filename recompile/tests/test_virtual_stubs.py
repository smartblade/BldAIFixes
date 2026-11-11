import unittest

from update_src.virtual_stubs import (
    _get_data_words, _match_defined_methods, find_own_vtable,
    get_object_files_starts)


class _Method:
    def __init__(self, proc_name):
        self.proc_name = proc_name
        self.is_destructor = proc_name.startswith("~")


class _SrcProcedure:
    def __init__(self, declaration):
        self.declaration = declaration


class TestVirtualStubs(unittest.TestCase):
    def test_own_vtable_is_last_stored_to_this(self):
        lines = [
            "push ebp",
            "mov ebp, esp",
            "mov dword ptr [ebp-004h], ecx",
            "mov eax, dword ptr [ebp-004h]",
            "mov dword ptr [eax], offset g005BD940",
            ";* String: \"x\"",
            "mov ecx, dword ptr [ebp-004h]",
            "mov dword ptr [ecx], offset g005BD93C",
            "mov edx, dword ptr [ebp-004h]",
            "add edx, 000000098h",
            "mov dword ptr [ebp-008h], edx",
            "mov eax, dword ptr [ebp-008h]",
            "mov dword ptr [eax], offset g005BD918",
        ]
        self.assertEqual(0x005BD93C, find_own_vtable(lines))

    def test_no_vtable(self):
        self.assertIsNone(find_own_vtable(["mov ebp, esp"]))

    def test_data_words(self):
        lines = [
            "g005BDB70  dd l004380E0",
            "           dd l00431B8B",
            "g005BDB78  dd 000000000h",
            "           dd l00438CF0",
            "g005BDB80  db 000h",
            "           dd l00438880",
        ]
        self.assertEqual(
            {0x005BDB70: 0x004380E0, 0x005BDB74: 0x00431B8B,
             0x005BDB7C: 0x00438CF0},
            _get_data_words(lines))

    def test_defined_methods_match_vtable(self):
        methods = [_Method("~B_Node"), _Method("Put"), _Method("Get")]
        entries = [0x10, 0x20, 0x30]
        src = {
            0x10: _SrcProcedure("B_Node::~B_Node()"),
            0x30: _SrcProcedure("int B_Node::Get()"),
        }
        self.assertTrue(_match_defined_methods(methods, entries, src))
        src[0x20] = _SrcProcedure("int B_Node::Get()")
        self.assertFalse(_match_defined_methods(methods, entries, src))

    def test_object_files_starts(self):
        lines = [
            "l004B4600 PROC",
            "           ret 00004h",
            "l004B4600 ENDP",
            ";",
            "           int 03h",
            "           int 03h",
            "l004B4680 PROC",
            "           ret",
            "l004B4680 ENDP",
            "l004B4690 PROC",
            "           ret",
            "l004B4690 ENDP",
            "           int 03h",
            "l004B46A8 PROC",
        ]
        self.assertEqual([0x004B4680], get_object_files_starts(lines))

    def test_vtables_of_bases_and_class(self):
        from update_src.virtual_stubs import find_vtables
        lines = [
            "mov dword ptr [ebp-004h], ecx",
            "mov eax, dword ptr [ebp-004h]",
            "mov dword ptr [eax], offset g005BE4A8",
            "mov ecx, dword ptr [ebp-004h]",
            "mov dword ptr [ecx], offset g005BE480",
        ]
        self.assertEqual([0x005BE4A8, 0x005BE480], find_vtables(lines))
