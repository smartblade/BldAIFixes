import unittest

import data_types
import expressions
from patterns.high_level.transform_procedure_call import \
    transform_procedure_call
from patterns.make_proc_decl_from_args import make_proc_decl_from_args


def _transform_call(name):
    args = [expressions.Identifier(data_types.Int32(), "size")]
    pc = expressions.ProcedureCall(
        name=name, arguments=args, proc_decl=make_proc_decl_from_args(args))
    return transform_procedure_call(
        pc, analysis=None, declarations=None, file_declarations=None,
        call_args_matcher=None)


class TestOperatorNewDelete(unittest.TestCase):
    def test_runtime_operators(self):
        self.assertEqual(
            "operator new(size)", _transform_call("??2@YAPAXI@Z").emit_code())
        self.assertEqual(
            "operator delete(size)",
            _transform_call("??3@YAXPAX@Z").emit_code())

    def test_smartheap_operators(self):
        self.assertEqual(
            "operator new(size)", _transform_call("shi_new").emit_code())
        self.assertEqual(
            "operator delete(size)",
            _transform_call("shi_delete").emit_code())
