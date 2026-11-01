import unittest

import data_types
import expressions
from patterns.high_level.transform_reinterpret import \
    _transform_to_static_cast


class TestIntStaticCast(unittest.TestCase):
    def test_signed_to_unsigned(self):
        e = _transform_to_static_cast(
            data_types.UInt32(),
            expressions.Identifier(data_types.Int32(), "count"))
        self.assertEqual("static_cast<unsigned int>(count)", e.emit_code())

    def test_unsigned_to_signed(self):
        e = _transform_to_static_cast(
            data_types.Int32(),
            expressions.Identifier(data_types.UInt32(), "size"))
        self.assertEqual("static_cast<int>(size)", e.emit_code())
