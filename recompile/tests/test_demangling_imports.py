import unittest

import data_types
import parser


class TestDemanglingImports(unittest.TestCase):
    def setUp(self):
        self.declared_types = {
            "B_MessageManager": data_types.ClassType("B_MessageManager", {})}

    def test_vararg_procedure(self):
        proc_decl = parser.demangle_cpp(
            "?vararg@@YAPBDPBDZZ", self.declared_types)
        self.assertEqual("vararg", proc_decl.proc_name)
        self.assertTrue(proc_decl.is_vararg)
        self.assertEqual(1, len(proc_decl.get_parameters_ids()))

    def test_operator(self):
        proc_decl = parser.demangle_cpp(
            "??6@YAAAVB_MessageManager@@AAV0@PBD@Z", self.declared_types)
        self.assertEqual("<<", proc_decl.operator.value)

    def test_global_variable(self):
        data_type, name = parser.demangle_cpp_variable(
            "?mout@@3VB_MessageManager@@A", self.declared_types)
        self.assertEqual("mout", name)
        self.assertEqual("B_MessageManager", data_type.class_name)

    def test_procedure_is_not_variable(self):
        self.assertIsNone(parser.demangle_cpp_variable(
            "?vararg@@YAPBDPBDZZ", self.declared_types))


class TestInstancesOfTemplates(unittest.TestCase):
    def test_parent_instance(self):
        # Each instance of a template is a separate class object
        parent = data_types.ClassType("B_PtrArray<B_Sector>", {})
        same_instance = data_types.ClassType("B_PtrArray<B_Sector>", {})
        child = data_types.ClassType("B_Map", {})
        child.set_parent(parent)
        self.assertTrue(data_types.are_compatible(
            data_types.Pointer32(child), data_types.Pointer32(same_instance)))
