import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
from procedure_declaration import ProcedureDeclaration


class TestCProcedures(unittest.TestCase):
    def test_element_of_array_of_pointers(self):
        rows = expressions.Identifier(
            data_types.Pointer32(data_types.Pointer32(data_types.UChar())),
            "rows")
        self.assertEqual(
            "rows[1]", do_pointer_dereference(rows, 4, None).emit_code())
        self.assertIsNone(do_pointer_dereference(rows, 2, None))

    def test_signed_constant(self):
        c = expressions.Constant(data_types.Int32(), -1)
        e = expressions.do_reinterpret(data_types.Long32(), c)
        self.assertEqual(-1, e.value)

    def test_call_of_static_function(self):
        proc_decl = ProcedureDeclaration(
            "start_pass", CallingConvention.CDECL, None,
            [(data_types.Int32(), "mode")], None, is_static=True)
        pc = expressions.ProcedureCall(
            name="start_pass", proc_decl=proc_decl,
            arguments=[expressions.Identifier(data_types.Int32(), "m")])
        self.assertEqual("start_pass(m)", pc.emit_code())
