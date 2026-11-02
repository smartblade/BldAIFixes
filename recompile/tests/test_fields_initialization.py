import unittest

import data_types
from patterns.high_level.fields_initialization import _go_to_field
from patterns.high_level.get_fields import get_fields


class _Method:
    is_virtual = True
    is_destructor = True
    proc_name = "~B_Base"


def _leaf():
    base = data_types.ClassType("B_Base", {})
    base.add_method(_Method())
    leaf = data_types.ClassType("B_Leaf", {
        4: (data_types.Pointer32(data_types.Int32()), "items"),
    })
    leaf.set_parent(base)
    return leaf


class TestFieldsInitialization(unittest.TestCase):
    def test_fields_after_parent_with_virtual_table(self):
        fields = get_fields(_leaf())
        self.assertEqual([None, "items"], [name for t, name in fields])

    def test_field_after_implicitly_constructed_parent(self):
        fields = get_fields(_leaf())
        items_type, items_name = fields[1]
        self.assertEqual(2, _go_to_field(0, fields, (items_type, "items")))
