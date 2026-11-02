import unittest

import data_types
import expressions
import instructions
from patterns.high_level.analysis.locals import LocalsAnalysis


class TestNamedFlagVariables(unittest.TestCase):
    def _fill(self, names, is_final):
        stackvar = expressions.intermediate.Stackvar(-8, 4)
        analysis = LocalsAnalysis()
        analysis.process_assignment(
            stackvar, expressions.Constant(data_types.Unknown32(), 0))
        analysis.collect_stack_accesses(
            [instructions.CodeInstruction(stackvar)])
        stack_vars = {}
        analysis.fill_stack_variables(stack_vars, names, is_final=is_final)
        return stack_vars

    def test_named_variable_is_int(self):
        stack_vars = self._fill({-8: "intersects"}, True)
        self.assertEqual("int", stack_vars[-8].data_type.get_type_name())

    def test_not_final_types(self):
        self.assertEqual({}, self._fill({-8: "intersects"}, False))

    def test_unnamed_variable(self):
        self.assertEqual({}, self._fill({}, True))
