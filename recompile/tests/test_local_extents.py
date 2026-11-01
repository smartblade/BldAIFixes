import unittest

import data_types
import expressions
import instructions
from patterns.high_level.analysis.locals import LocalsAnalysis


def _analyse(variable_offset, typed_local):
    vector = data_types.ClassType("B_Vector", {
        0: (data_types.Double(), "x"),
        8: (data_types.Double(), "y"),
        16: (data_types.Double(), "z"),
    })
    analysis = LocalsAnalysis()
    local = expressions.intermediate.Local(-40)
    analysis.process_local(local)
    if typed_local:
        analysis.process_reinterpret(data_types.Pointer32(vector), local)
    analysis.on_transformation_finished()
    stackvar = expressions.intermediate.Stackvar(variable_offset, 4)
    analysis.process_assignment(
        stackvar, expressions.Identifier(data_types.Int32(), "value"))
    analysis.collect_stack_accesses([instructions.CodeInstruction(stackvar)])
    stack_vars = {}
    analysis.fill_stack_variables(stack_vars, {})
    return stack_vars


class TestLocalExtents(unittest.TestCase):
    def test_variable_above_typed_local(self):
        self.assertIn(-8, _analyse(-8, typed_local=True))

    def test_variable_above_untyped_local(self):
        self.assertNotIn(-8, _analyse(-8, typed_local=False))

    def test_variable_inside_typed_local(self):
        self.assertNotIn(-32, _analyse(-32, typed_local=True))
