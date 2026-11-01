import unittest

import data_types
import expressions
import instructions
from patterns.high_level.analysis.locals import LocalsAnalysis
from patterns.high_level.struct_variable_field import struct_variable_field


def _vector():
    return data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })


def _analyse(stackvar):
    vector = _vector()
    analysis = LocalsAnalysis()
    local = expressions.intermediate.Local(-40)
    analysis.process_local(local)
    analysis.process_reinterpret(data_types.Pointer32(vector), local)
    field_local = expressions.intermediate.Local(-32)
    analysis.process_local(field_local)
    analysis.process_access(field_local, 0, 8)
    analysis.on_transformation_finished()
    analysis.collect_stack_accesses([instructions.CodeInstruction(stackvar)])
    stack_vars = {}
    analysis.fill_stack_variables(stack_vars, {})
    return stack_vars


class TestStructLocals(unittest.TestCase):
    def test_struct_variable(self):
        stack_vars = _analyse(expressions.intermediate.Stackvar(-40, 8))
        self.assertEqual("B_Vector", stack_vars[-40].data_type.class_name)
        self.assertEqual(
            "unknown_loc_28.x",
            struct_variable_field(stack_vars, -40, 8).emit_code())
        self.assertEqual(
            "unknown_loc_28.y",
            struct_variable_field(stack_vars, -32, None).emit_code())

    def test_access_inside_field(self):
        stack_vars = _analyse(expressions.intermediate.Stackvar(-36, 4))
        self.assertNotIn(-40, stack_vars)
