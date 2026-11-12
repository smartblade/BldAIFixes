import os
import tempfile
import unittest

from cpp_mangling import mangle_cpp
import parser
from patterns.procedure import Procedure
from update_src.make_metadata_header import make_metadata_header


class TestCppMangling(unittest.TestCase):
    """The tests of test_cpp_demangling.py in reverse: the declarations
    restored from the mangled names are mangled back."""

    def _assert_mangled(self, declaration, mangled_name):
        proc_decl = parser.demangle_cpp(mangled_name, {})
        # The declaration demangled by test_cpp_demangling.py
        self.assertEqual(declaration, proc_decl.get_declaration())
        self.assertEqual(mangled_name, mangle_cpp(proc_decl))

    def test_operator_shr(self):
        self._assert_mangled(
            "B_IDataFile &operator >>(B_IDataFile &arg_1, short &arg_2)",
            "??5@YAAAVB_IDataFile@@AAV0@AAF@Z")

    def test_operator_shl(self):
        self._assert_mangled(
            "B_ODataFile &operator <<("
            "B_ODataFile &arg_1, const double &arg_2)",
            "??6@YAAAVB_ODataFile@@AAV0@ABN@Z")

    def test_operator_mul(self):
        self._assert_mangled(
            "const B_Color &operator *(float arg_1) const",
            "??DB_Color@@QBEABV0@M@Z")

    def test_operator_add(self):
        self._assert_mangled(
            "const B_Name &operator +(const char *arg_1) const",
            "??HB_Name@@QBEABV0@PBD@Z")

    def test_operator_div(self):
        self._assert_mangled(
            "const B_Color &operator /(float arg_1) const",
            "??KB_Color@@QBEABV0@M@Z")

    def test_operator_ass(self):
        self._assert_mangled(
            "const B_Name &operator =(const B_Name &arg_1)",
            "??4B_Name@@QAEABV0@ABV0@@Z")

    def test_operator_add_ass(self):
        self._assert_mangled(
            "const B_Name &operator +=(const char *arg_1)",
            "??YB_Name@@QAEABV0@PBD@Z")

    def test_operator_lt(self):
        self._assert_mangled(
            "unsigned int operator <(const B_Name &arg_1) const",
            "??MB_Name@@QBEIABV0@@Z")

    def test_operator_gt(self):
        self._assert_mangled(
            "unsigned int operator >(const B_Name &arg_1) const",
            "??OB_Name@@QBEIABV0@@Z")

    def test_operator_eq(self):
        self._assert_mangled(
            "int operator ==(const B_MessageChannel &arg_1) const",
            "??8B_MessageChannel@@QBEHABV0@@Z")

    def test_operator_ne(self):
        self._assert_mangled(
            "unsigned int operator !=(const char *arg_1) const",
            "??9B_Name@@QBEIPBD@Z")

    def test_constructor(self):
        self._assert_mangled(
            "B_Color(unsigned char arg_1, unsigned char arg_2, "
            "unsigned char arg_3)",
            "??0B_Color@@QAE@EEE@Z")

    def test_constructor_with_class_parameter(self):
        self._assert_mangled(
            "B_ChannelOFile(B_Name arg_1, const char *arg_2)",
            "??0B_ChannelOFile@@QAE@VB_Name@@PBD@Z")

    def test_constructor_with_enum_parameter(self):
        self._assert_mangled(
            "B_BitMap(BitMapType arg_1, unsigned int arg_2, "
            "unsigned int arg_3, const B_Pal *arg_4)",
            "??0B_BitMap@@QAE@W4BitMapType@0@IIPBVB_Pal@@@Z")

    def test_declared_types_are_not_needed(self):
        declared_types = {}
        proc_decl = parser.demangle_cpp(
            "??0B_BitMap@@QAE@W4BitMapType@0@IIPBVB_Pal@@@Z", declared_types)
        declared_types.clear()

        self.assertEqual(
            "??0B_BitMap@@QAE@W4BitMapType@0@IIPBVB_Pal@@@Z",
            mangle_cpp(proc_decl))

    def test_virtual_destructor(self):
        self._assert_mangled("virtual ~B_List()", "??1B_List@@UAE@XZ")

    def test_default_constructor_closure(self):
        self._assert_mangled(
            "void default constructor closure()", "??_FB_List@@QAEXXZ")

    def test_method(self):
        self._assert_mangled(
            "long Seek(long arg_1, int arg_2)",
            "?Seek@B_IDataFile@@QAEJJH@Z")

    def test_private_method(self):
        self._assert_mangled(
            "void WriteCacheBlock()",
            "?WriteCacheBlock@B_ODataFile@@AAEXXZ")

    def test_static_method(self):
        self._assert_mangled(
            "static B_Resource *Load(B_IDataFile &arg_1, "
            "unsigned short arg_2)",
            "?Load@B_Resource@@SAPAV1@AAVB_IDataFile@@G@Z")

    def test_virtual_const_method(self):
        self._assert_mangled(
            "virtual unsigned long CheckSum() const",
            "?CheckSum@B_ObjDscr@@UBEKXZ")

    def test_back_references(self):
        self._assert_mangled(
            "PyObject *CallPythonObject(PyObject *arg_1, PyObject *arg_2)",
            "?CallPythonObject@@YAPAUPyObject@@PAU1@0@Z")

    def test_scalar_deleting_destructor(self):
        proc_decl = parser.demangle_cpp("??_GB_OctantNodeBase@@UAEPAXI@Z", {})
        self.assertTrue(proc_decl.is_scalar_deleting_destructor)
        self.assertEqual(
            "??_GB_OctantNodeBase@@UAEPAXI@Z", mangle_cpp(proc_decl))

    def test_names_of_parameters_are_not_mangled(self):
        proc_decl = parser.demangle_cpp(
            "?CollectSectorsInBox@LeafNode@@UAEXABVB_BoundingBox@@"
            "PAVB_OctTreeSectorsList@@N@Z", {})
        param_ids = list(proc_decl.get_parameters_ids().values())[1:]
        names = ["__", "outList", "__"]
        proc_decl = proc_decl.copy(parameters=[
            (param_id.data_type, name)
            for param_id, name in zip(param_ids, names)
        ])
        self.assertEqual(
            "virtual void CollectSectorsInBox("
            "const B_BoundingBox &, B_OctTreeSectorsList *outList, double)",
            proc_decl.get_declaration())
        self.assertEqual(
            "?CollectSectorsInBox@LeafNode@@UAEXABVB_BoundingBox@@"
            "PAVB_OctTreeSectorsList@@N@Z",
            mangle_cpp(proc_decl))


_header = """
template<class TYPE>
class array_t
{
public:
    TYPE *elements;
};

struct B_Point
{
    int x;
};

class B_Sector;

class B_Node
{
    virtual int Hidden();
public:
    virtual int Count(array_t<B_Sector *> *sectors, int index);
    virtual void Move(B_Point *point, B_Point *other);
protected:
    virtual int Weight() const;
};
"""


class TestCppManglingOfHeaders(unittest.TestCase):
    """Methods declared in headers, like the stubs of virtual methods."""

    @staticmethod
    def _mangled_methods():
        with tempfile.TemporaryDirectory() as src_dir:
            with open(os.path.join(src_dir, "test.h"), "w") as f:
                f.write(_header)
            node = parser.parse_cpp_header(src_dir)[1]["B_Node"]
        return dict(
            (method.proc_name, mangle_cpp(method))
            for method in node.virtual_methods)

    def test_access_of_methods(self):
        mangled = self._mangled_methods()
        self.assertEqual("?Hidden@B_Node@@EAEHXZ", mangled["Hidden"])
        self.assertEqual("?Weight@B_Node@@MBEHXZ", mangled["Weight"])

    def test_template_instance(self):
        self.assertEqual(
            "?Count@B_Node@@UAEHPAV?$array_t@PAVB_Sector@@@@H@Z",
            self._mangled_methods()["Count"])

    def test_struct(self):
        self.assertEqual(
            "?Move@B_Node@@UAEXPAUB_Point@@0@Z",
            self._mangled_methods()["Move"])


class TestVirtualStubMetadata(unittest.TestCase):
    def test_mangled_name_of_virtual_stub(self):
        proc_decl = parser.demangle_cpp("?Seek@B_IDataFile@@QAEJJH@Z", {})
        procedure = Procedure(None, 0x10001000, proc_decl, [], None)

        metadata = make_metadata_header(
            procedure, False, "BBLibc.dll", {}, is_virtual_stub=True)

        self.assertIn(
            "* VC++ mangling:          ?Seek@B_IDataFile@@QAEJJH@Z",
            metadata)

    def test_no_mangled_name_of_other_procedure(self):
        proc_decl = parser.demangle_cpp("?Seek@B_IDataFile@@QAEJJH@Z", {})
        procedure = Procedure(None, 0x10001000, proc_decl, [], None)

        metadata = make_metadata_header(procedure, False, "BBLibc.dll", {})

        self.assertNotIn("VC++ mangling", metadata)
