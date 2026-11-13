import os
import tempfile
import unittest

import parser

_header = """
class B_Vector
{
public:
    B_Vector()
    :
    x(0.0), y(0.0), z(0.0)
    {
    }

    B_Vector(double x, double y, double z)
    :
    x(x), y(y), z(z)
    {
    }

    double x;
    double y;
    double z;
};
"""


class TestDefaultInitializers(unittest.TestCase):
    def test_initializers_of_constructor_without_parameters(self):
        with tempfile.TemporaryDirectory() as src_dir:
            with open(os.path.join(src_dir, "test.h"), "w") as f:
                f.write(_header)
            vector = parser.parse_cpp_header(src_dir)[1]["B_Vector"]
        self.assertEqual(
            {"x": "0.0", "y": "0.0", "z": "0.0"},
            vector.default_initializers)
