import os
import tempfile
import unittest

import parser

_header = """
template<class TYPE>
class B_Array
{
public:
    virtual ~B_Array();
    TYPE **elements;
    unsigned int size;
};

template<class TYPE>
class B_ObjArray : public B_Array<TYPE>
{
};

class B_Pair
{
public:
    int a;
    int b;
};

class B_PairArray : public B_Array<B_Pair>
{
};

class B_Holder
{
public:
    B_ObjArray<B_Pair> pairs;
    B_PairArray otherPairs;
    int type;
};
"""


def _parse_types():
    with tempfile.TemporaryDirectory() as src_dir:
        with open(os.path.join(src_dir, "test.h"), "w") as f:
            f.write(_header)
        return parser.parse_cpp_header(src_dir)[1]


class TestClassSize(unittest.TestCase):
    def test_class_without_fields_has_size_of_base(self):
        types = _parse_types()
        self.assertEqual(12, types["B_PairArray"].size)
        self.assertEqual(12, types["B_ObjArray"].size)

    def test_fields_of_classes_without_own_fields(self):
        types = _parse_types()
        holder = types["B_Holder"]
        self.assertEqual(
            [(0, "pairs"), (12, "otherPairs"), (24, "type")],
            [(offset, name) for offset, (_, name) in
             sorted(holder.fields.items())])
        self.assertEqual(28, holder.size)
