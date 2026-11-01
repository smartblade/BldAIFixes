import unittest

import data_types
import expressions
import instructions
from patterns.high_level.analysis.locals import LocalsAnalysis


class TestRefinedLocals(unittest.TestCase):
    def test_unknown_type_is_refined(self):
        item = data_types.ClassType("B_Item", {0: (data_types.Int32(), "a")})
        stackvar = expressions.intermediate.Stackvar(-8, 4)
        analysis = LocalsAnalysis()
        analysis.process_assignment(
            stackvar, expressions.Identifier(data_types.Unknown32(), "u"))
        analysis.collect_stack_accesses(
            [instructions.CodeInstruction(stackvar)])
        stack_vars = {}
        self.assertFalse(analysis.fill_stack_variables(stack_vars, {}))
        # Type becomes known in later transformations
        analysis.process_assignment(
            stackvar,
            expressions.Identifier(data_types.Pointer32(item), "item"))
        self.assertTrue(analysis.fill_stack_variables(stack_vars, {}))
        self.assertEqual(
            "B_Item *", stack_vars[-8].data_type.get_type_name())
        self.assertFalse(analysis.fill_stack_variables(stack_vars, {}))
