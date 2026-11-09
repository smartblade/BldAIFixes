import unittest

import data_types
import parser


class TestCppVariableDeclaration(unittest.TestCase):
    def test_extern_variable(self):
        var_type, var_name = parser.parse_cpp_variable_declaration(
            "extern unsigned int gbl_node_count",
            {"unsigned int": data_types.UInt32()},
        )
        self.assertIsInstance(var_type, data_types.UInt32)
        self.assertEqual("gbl_node_count", var_name)

    def test_array_of_arrays(self):
        var_type, var_name = parser.parse_cpp_variable_declaration(
            "double m[4][2]", {"double": data_types.Double()})
        self.assertEqual("m", var_name)
        self.assertIsInstance(var_type, data_types.Array)
        self.assertEqual(4, var_type.length)
        self.assertIsInstance(var_type.element_type, data_types.Array)
        self.assertEqual(2, var_type.element_type.length)
        self.assertEqual(64, var_type.size)
