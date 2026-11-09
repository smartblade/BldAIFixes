import unittest

from get_procedure_declaration_at import get_procedures_declarations
from make_tuple import make_tuple


class TestGetProceduresDeclarations(unittest.TestCase):
    def test_demangle_before_parsing_declarations_from_sources(self):
        # B_Foo is known only from the mangled name of the procedure
        # at the greater address
        src_declaration = make_tuple(
            "CppDeclaration",
            class_name=None,
            declaration="void Baz(B_Foo &foo)",
        )
        declarations = make_tuple(
            "Declarations",
            symbols=make_tuple(
                "Symbols", procedures={0x10001000: src_declaration}),
            exported_procedures={0x10002000: "?Bar@@YAXAAVB_Foo@@@Z"},
            declared_types={},
        )

        procedures_declarations = get_procedures_declarations(
            declarations, [0x10001000, 0x10002000])

        self.assertEqual(
            "void Baz(B_Foo &foo)",
            procedures_declarations[0x10001000].get_declaration())
        self.assertEqual(
            "void Bar(B_Foo &arg_1)",
            procedures_declarations[0x10002000].get_declaration())
