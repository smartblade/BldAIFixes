import unittest

from patterns.annotate_import_jumps import annotate_import_jumps

LINES = [
    "l00401000 PROC\n",
    "           call l005BBD38\n",
    "           call l005BBD3D\n",
    "           call l00402000\n",
    "l00401000 ENDP\n",
    "l005BBD38 PROC\n",
    "           jmp near ptr l005BBD5C\n",
    "l005BBD3D: jmp near ptr l005BBD56\n",
    "l005BBD56: jmp [__imp_shi_delete]; [SHW32.shi_delete].\n",
    "l005BBD5C: jmp [__imp_shi_new]; [SHW32.shi_new].\n",
    "l00402000: ret\n",
]


class TestAnnotateImportJumps(unittest.TestCase):
    def test_calls_of_jumps_to_imports(self):
        lines = annotate_import_jumps(LINES)
        self.assertEqual(
            "           call l005BBD38; [SHW32.shi_new].\n", lines[1])
        self.assertEqual(
            "           call l005BBD3D; [SHW32.shi_delete].\n", lines[2])

    def test_call_of_procedure(self):
        lines = annotate_import_jumps(LINES)
        self.assertEqual("           call l00402000\n", lines[3])
