import os
import tempfile
import unittest

import parser

_header = """
template<class TYPE>
class B_PtrArray
{
public:
    virtual ~B_PtrArray();
    TYPE **elements;
    unsigned int size;
};

class B_Item
{
public:
    int value;
};

class B_Base
{
public:
    virtual int GetTypeID() = 0;
};

class B_Items : public B_PtrArray<B_Item>
{
};

class B_Node : public B_Base, public B_PtrArray<B_Item>
{
public:
    virtual int GetTypeID();
};
"""


def _parse_types():
    with tempfile.TemporaryDirectory() as src_dir:
        with open(os.path.join(src_dir, "test.h"), "w") as f:
            f.write(_header)
        return parser.parse_cpp_header(src_dir)[1]


class TestClassParents(unittest.TestCase):
    def test_template_parent(self):
        items = _parse_types()["B_Items"]
        self.assertEqual("B_PtrArray<B_Item>", items.parent.class_name)
        field_type, field_name = items.get_field_by_offset(4)
        self.assertEqual("elements", field_name)
        self.assertEqual("B_Item **", field_type.get_type_name())

    def test_multiple_inheritance(self):
        node = _parse_types()["B_Node"]
        self.assertEqual("B_Base", node.parent.class_name)
        # Virtual table of the second parent is at offset 4
        field_type, field_name = node.get_field_by_offset(8)
        self.assertEqual("elements", field_name)
        self.assertEqual("B_Item **", field_type.get_type_name())
        self.assertEqual("size", node.get_field_by_offset(12)[1])
