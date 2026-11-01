import unittest

import data_types
import parser


class TestTemplateInstantiation(unittest.TestCase):
    def test_fields_of_instantiated_template(self):
        param = data_types.ClassType("TYPE", {})
        array = data_types.ClassType("B_PtrArray", {
            0: (data_types.Pointer32(data_types.Pointer32(param)),
                "elements"),
            4: (data_types.UInt32(), "size"),
        })
        array.template_param = param
        sector = data_types.ClassType("B_Sector", {})
        classes = {"TYPE": param, "B_PtrArray": array, "B_Sector": sector}
        instance = parser.parse_data_type("B_PtrArray<B_Sector>", classes)
        self.assertEqual("B_PtrArray<B_Sector>", instance.class_name)
        elements_type, name = instance.get_field_by_offset(0)
        self.assertEqual("elements", name)
        self.assertEqual("B_Sector **", elements_type.get_type_name())
        self.assertEqual(8, instance.size)
