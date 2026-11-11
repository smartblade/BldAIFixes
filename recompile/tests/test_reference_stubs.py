import unittest

import data_types
from procedure_declaration import ProcedureDeclaration
from update_src.writer import _make_stub_instructions
from writer import Writer


def _emit(instrs):
    writer = Writer()
    for instr in instrs:
        instr.emit_code(writer)
    return writer.get_string()


class TestReferenceStubs(unittest.TestCase):
    def _method(self, class_type, return_type):
        return ProcedureDeclaration(
            "Get", None, class_type, [], data_types.Reference(return_type))

    def test_field_of_the_returned_type(self):
        matrix = data_types.ClassType("B_Matrix", {0: (data_types.Int32(), "a")})
        owner = data_types.ClassType("B_Owner", {8: (matrix, "pose")})
        self.assertEqual(
            "return this->pose;\n",
            _emit(_make_stub_instructions(self._method(owner, matrix))))

    def test_static_variable(self):
        box = data_types.ClassType("B_BoundingBox", {0: (data_types.Int32(), "a")})
        owner = data_types.ClassType("B_Owner", {8: (data_types.Int32(), "x")})
        self.assertEqual(
            "static B_BoundingBox stub;\nreturn stub;\n",
            _emit(_make_stub_instructions(self._method(owner, box))))
