import os
import tempfile
import unittest

from parser.cpp_headers import parse_cpp_header


class TestOtherMethods(unittest.TestCase):
    def test_inline_method_is_found(self):
        header = """class B_Vector
{
public:
    double x;
};

class B_Plane
{
public:
    virtual ~B_Plane()
    {
    }

    double Distance(const B_Vector *point) const
    {
        return this->p + point->x * this->normal.x;
    }

    void Set(int a);
    void Set(double a);

    B_Vector normal;
    double p;
};
"""
        with tempfile.TemporaryDirectory() as src_dir:
            with open(os.path.join(src_dir, "Plane.h"), "w") as f:
                f.write(header)
            declared_types = parse_cpp_header(src_dir)[1]
        plane = declared_types["B_Plane"]
        distance = plane.find_other_method("Distance")
        self.assertIsNotNone(distance)
        self.assertTrue(distance.is_const)
        # Overloaded methods are not found
        self.assertIsNone(plane.find_other_method("Set"))
        # Not virtual methods don't change fields
        self.assertEqual(
            ["normal", "p"],
            [name for offset, (data_type, name)
             in sorted(plane.fields.items())])
