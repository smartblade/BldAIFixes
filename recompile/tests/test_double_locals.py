import unittest

import data_types
import expressions
from patterns.high_level.analysis.locals import LocalsAnalysis


def _analyse(*stackvars):
    analysis = LocalsAnalysis()
    value = expressions.Identifier(data_types.Double(), "value")
    analysis.process_assignment(
        expressions.intermediate.Stackvar(-8, 8), value)
    analysis.process_stackvar(-8, 8)
    for offset, size in stackvars:
        analysis.process_stackvar(offset, size)
    stack_vars = {}
    analysis.fill_stack_variables(stack_vars, {})
    return stack_vars


class TestDoubleLocals(unittest.TestCase):
    def test_double_variable(self):
        stack_vars = _analyse()
        self.assertEqual("unknown_loc_08", stack_vars[-8].name)
        self.assertIsInstance(stack_vars[-8].data_type, data_types.Double)

    def test_half_of_double(self):
        self.assertNotIn(-8, _analyse((-4, 4)))

    def test_double_accessed_as_int(self):
        self.assertNotIn(-8, _analyse((-8, 4)))
