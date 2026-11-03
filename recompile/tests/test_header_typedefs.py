import os
import tempfile
import unittest

import parser

_header = """
struct jpeg_compress_struct;
typedef struct jpeg_compress_struct * j_compress_ptr;
typedef unsigned int JDIMENSION;
typedef unsigned char JSAMPLE;
typedef JSAMPLE *JSAMPROW;
typedef short JCOEF;
typedef JCOEF JBLOCK[64];
typedef void (*unparsed_method) (j_compress_ptr cinfo);
"""

_source = """
/*
* Module:                 BBLibc.dll
* Entry point:            0x100096A0
*/

void jpeg_suppress_tables(j_compress_ptr cinfo, int suppress)
{
}
"""


def _parse(files):
    with tempfile.TemporaryDirectory() as src_dir:
        for name, text in files.items():
            with open(os.path.join(src_dir, name), "w") as f:
                f.write(text)
        types = parser.parse_cpp_header(src_dir)[1]
        symbols = parser.SrcSymbols.collect(src_dir)
        return types, symbols


class TestHeaderTypedefs(unittest.TestCase):
    def test_typedefs(self):
        types, symbols = _parse({"jpeglib.h": _header})
        self.assertEqual(
            "j_compress_ptr", types["j_compress_ptr"].get_type_name())
        self.assertEqual(
            "jpeg_compress_struct",
            types["j_compress_ptr"].pointee.class_name)
        self.assertEqual(4, types["JDIMENSION"].size)
        self.assertEqual(
            "JSAMPLE", types["JSAMPROW"].pointee.get_type_name())
        self.assertEqual(128, types["JBLOCK"].size)
        self.assertNotIn("unparsed_method", types)

    def test_procedures_of_c_files(self):
        types, symbols = _parse(
            {"jpeglib.h": _header, "jcapimin.c": _source})
        procedure = symbols["BBLibc.dll"].procedures[0x100096A0]
        self.assertEqual("_jpeg_suppress_tables", procedure.mangled_name)
