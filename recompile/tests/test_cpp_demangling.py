import unittest

import parser


class TestCppDemangling(unittest.TestCase):
    @staticmethod
    def _declaration(mangled_name):
        return parser.demangle_cpp(mangled_name, {}).get_declaration()

    def test_operator_shr(self):
        self.assertEqual(
            "B_IDataFile &operator >>(B_IDataFile &arg_1, short &arg_2)",
            self._declaration("??5@YAAAVB_IDataFile@@AAV0@AAF@Z"))

    def test_operator_shl(self):
        self.assertEqual(
            "B_ODataFile &operator <<("
            "B_ODataFile &arg_1, const double &arg_2)",
            self._declaration("??6@YAAAVB_ODataFile@@AAV0@ABN@Z"))

    def test_operator_mul(self):
        self.assertEqual(
            "const B_Color &operator *(float arg_1) const",
            self._declaration("??DB_Color@@QBEABV0@M@Z"))

    def test_operator_add(self):
        self.assertEqual(
            "const B_Name &operator +(const char *arg_1) const",
            self._declaration("??HB_Name@@QBEABV0@PBD@Z"))

    def test_operator_div(self):
        self.assertEqual(
            "const B_Color &operator /(float arg_1) const",
            self._declaration("??KB_Color@@QBEABV0@M@Z"))

    def test_operator_ass(self):
        self.assertEqual(
            "const B_Name &operator =(const B_Name &arg_1)",
            self._declaration("??4B_Name@@QAEABV0@ABV0@@Z"))

    def test_operator_add_ass(self):
        self.assertEqual(
            "const B_Name &operator +=(const char *arg_1)",
            self._declaration("??YB_Name@@QAEABV0@PBD@Z"))

    def test_operator_lt(self):
        self.assertEqual(
            "unsigned int operator <(const B_Name &arg_1) const",
            self._declaration("??MB_Name@@QBEIABV0@@Z"))

    def test_operator_gt(self):
        self.assertEqual(
            "unsigned int operator >(const B_Name &arg_1) const",
            self._declaration("??OB_Name@@QBEIABV0@@Z"))

    def test_operator_eq(self):
        self.assertEqual(
            "int operator ==(const B_MessageChannel &arg_1) const",
            self._declaration("??8B_MessageChannel@@QBEHABV0@@Z"))

    def test_operator_ne(self):
        self.assertEqual(
            "unsigned int operator !=(const char *arg_1) const",
            self._declaration("??9B_Name@@QBEIPBD@Z"))

    def test_constructor(self):
        self.assertEqual(
            "B_Color(unsigned char arg_1, unsigned char arg_2, "
            "unsigned char arg_3)",
            self._declaration("??0B_Color@@QAE@EEE@Z"))

    def test_constructor_with_class_parameter(self):
        self.assertEqual(
            "B_ChannelOFile(B_Name arg_1, const char *arg_2)",
            self._declaration("??0B_ChannelOFile@@QAE@VB_Name@@PBD@Z"))

    def test_constructor_with_undeclared_enum_parameter(self):
        self.assertEqual(
            "B_BitMap(BitMapType arg_1, unsigned int arg_2, "
            "unsigned int arg_3, const B_Pal *arg_4)",
            self._declaration(
                "??0B_BitMap@@QAE@W4BitMapType@0@IIPBVB_Pal@@@Z"))

    def test_undeclared_types_become_declared(self):
        declared_types = {}

        parser.demangle_cpp(
            "??0B_BitMap@@QAE@W4BitMapType@0@IIPBVB_Pal@@@Z", declared_types)

        self.assertEqual(
            {"B_BitMap", "B_BitMap::BitMapType", "B_Pal"},
            set(
                data_type.make_variable_declaration(None)
                for data_type in declared_types.values()
            ))

    def test_virtual_destructor(self):
        self.assertEqual(
            "virtual ~B_List()",
            self._declaration("??1B_List@@UAE@XZ"))

    def test_default_constructor_closure(self):
        self.assertEqual(
            "void default constructor closure()",
            self._declaration("??_FB_List@@QAEXXZ"))

    def test_method(self):
        self.assertEqual(
            "long Seek(long arg_1, int arg_2)",
            self._declaration("?Seek@B_IDataFile@@QAEJJH@Z"))

    def test_private_method(self):
        self.assertEqual(
            "void WriteCacheBlock()",
            self._declaration("?WriteCacheBlock@B_ODataFile@@AAEXXZ"))

    def test_static_method(self):
        self.assertEqual(
            "static B_Resource *Load(B_IDataFile &arg_1, "
            "unsigned short arg_2)",
            self._declaration("?Load@B_Resource@@SAPAV1@AAVB_IDataFile@@G@Z"))

    def test_virtual_const_method(self):
        self.assertEqual(
            "virtual unsigned long CheckSum() const",
            self._declaration("?CheckSum@B_ObjDscr@@UBEKXZ"))

    def test_back_references(self):
        self.assertEqual(
            "PyObject *CallPythonObject(PyObject *arg_1, PyObject *arg_2)",
            self._declaration("?CallPythonObject@@YAPAUPyObject@@PAU1@0@Z"))

    def test_scalar_deleting_destructor(self):
        proc_decl = parser.demangle_cpp("??_GB_OctantNodeBase@@UAEPAXI@Z", {})
        self.assertTrue(proc_decl.is_scalar_deleting_destructor)
        self.assertEqual("B_OctantNodeBase", proc_decl.method_class.class_name)
        self.assertEqual(4, proc_decl.stack_delta)

    def test_not_mangled_name(self):
        self.assertIsNone(parser.demangle_cpp("initBBLibc", {}))
