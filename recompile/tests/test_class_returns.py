import os
import tempfile
import unittest

import expressions
import instructions
import parser
from patterns.high_level.transform_class_returns import \
    transform_class_returns

_header = """
class B_Vector
{
public:
    B_Vector(double x, double y)
    :
    x(x), y(y)
    {
    }

    B_Vector operator -(const B_Vector &that) const;

    double x;
    double y;
};
"""


def _parse_vector():
    with tempfile.TemporaryDirectory() as src_dir:
        with open(os.path.join(src_dir, "test.h"), "w") as f:
            f.write(_header)
        return parser.parse_cpp_header(src_dir)[1]["B_Vector"]


class _ProcDecl:
    def __init__(self, return_type):
        self.return_type = return_type


class TestClassReturns(unittest.TestCase):
    def test_constructor_is_parsed(self):
        vector = _parse_vector()
        self.assertEqual(1, len(vector.constructors))

    def test_return_of_constructed_fields(self):
        vector = _parse_vector()
        result = expressions.Identifier(None, "__result")
        x = expressions.Identifier(None, "a")
        y = expressions.Identifier(None, "b")
        regdef = instructions.TemporaryRegisterDefinition()
        regdef.define_reg_value("eax", result)
        instrs = transform_class_returns(_ProcDecl(vector), [
            instructions.Assignment(
                expressions.FieldAccess(result, "x"), x),
            instructions.Assignment(
                expressions.FieldAccess(result, "y"), y),
            regdef,
        ])
        self.assertEqual(1, len(instrs))
        self.assertEqual(
            "B_Vector(a, b)", instrs[0].expression.emit_code())
