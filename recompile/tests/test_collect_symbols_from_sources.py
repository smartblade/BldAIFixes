import unittest

from parser.collect_symbols_from_sources import SrcSymbols


class TestCollectSymbolsFromSources(unittest.TestCase):
    def test_comment_before_definition(self):
        procedures = SrcSymbols.collect_procedures([
            "/*\n",
            "* Module:                 Blade.exe\n",
            "* Entry point:            0x0045327B\n",
            "*/\n",
            "\n",
            "// TODO double check\n",
            "int B_OctTreeSectorsList::BuildSurfaceCache()\n",
            "{\n",
            "}\n",
        ])
        self.assertEqual(
            "int B_OctTreeSectorsList::BuildSurfaceCache()",
            procedures[("Blade.exe", 0x0045327B)].declaration.strip())

    def test_comment_in_body(self):
        procedures = SrcSymbols.collect_procedures([
            "/*\n",
            "* Module:                 Blade.exe\n",
            "* Entry point:            0x00405050\n",
            "*/\n",
            "\n",
            "void B_Matrix::Set()\n",
            "{\n",
            "    /* a comment\n",
            "     * of two lines */\n",
            "    m = 0;\n",
            "}\n",
        ])
        definition = procedures[("Blade.exe", 0x00405050)]
        self.assertEqual(4, definition.definition_start_line)
        self.assertEqual(10, definition.definition_end_line)
