from calling_convention import CallingConvention
import data_types
from procedure_declaration import ProcedureDeclaration


def demangle_cpp(s, declared_types):
    demangler = _CppDemangler(s, declared_types)
    return demangler.parse()


def demangle_cpp_variable(s, declared_types):
    """Return (data type, name) of a mangled global variable, e.g.
    '?mout@@3VB_MessageManager@@A', or None."""
    demangler = _CppDemangler(s, declared_types)
    return demangler.parse_variable()


class _Operator:
    def __init__(self, name=None, is_constructor=False, is_destructor=False):
        self._name = name
        self._is_constructor = is_constructor
        self._is_destructor = is_destructor

    def make_name(self, class_name):
        if self.is_constructor:
            return "{}".format(class_name)
        if self.is_destructor:
            return "~{}".format(class_name)
        return  self._name

    @property
    def is_constructor(self):
        return self._is_constructor

    @property
    def is_destructor(self):
        return self._is_destructor


class _CppDemangler:
    def __init__(self, s, declared_types):
        self._pos = 0
        self._decl_str = s
        self._declared_types = declared_types
        self._names = []

    def parse(self):
        if not self._try_pop_char("?"):
            return None
        method_class, proc_name, operator = self._pop_procedure_qualified_name()
        is_method, is_static, is_virtual, modifier = self._pop_modifier()
        is_const = False
        if is_method and not is_static:
            is_const = self._pop_const_modifier() == "const"
        calling_convention = self._pop_calling_convention()
        if (
            operator is not None and
            (operator.is_constructor or operator.is_destructor)
        ):
            return_type = None
            self._expect("@")
        else:
            return_type = self._pop_data_type()
        parameters = []
        is_vararg = False
        if not self._try_pop_char("X"):
            arg_types = []
            while not self._try_pop_char("@"):
                # 'Z' ends parameters followed by '...'
                if self._try_pop_char("Z"):
                    is_vararg = True
                    break
                parameter_type = self._pop_data_type(arg_types)
                parameters.append((parameter_type, None))
        self._expect("Z")
        return ProcedureDeclaration(
            proc_name, calling_convention, method_class, parameters,
            return_type, is_static=is_static, is_virtual=is_virtual,
            is_vararg=is_vararg, is_const=is_const)

    def parse_variable(self):
        if not self._try_pop_char("?"):
            return None
        name = self._pop_identifier()
        if not self._try_pop_char("@"):
            return None
        # Global variable
        if not self._try_pop_char("3"):
            return None
        data_type = self._pop_data_type()
        if not self._try_pop_char("A"):
            return None
        if self._pos != len(self._decl_str):
            return None
        return data_type, name

    def _pop_procedure_qualified_name(self):
        if self._try_pop_char("?"):
            operator = self._pop_operator()
        else:
            operator = None
        class_name = None
        proc_name = None
        proc_names = self._pop_qualified_identifier()
        if operator is None:
            proc_name = proc_names.pop(0)
        if proc_names:
            class_name = proc_names.pop()
        assert len(proc_names) == 0
        if operator is not None:
            assert proc_name is None
            proc_name = operator.make_name(class_name)
        if not class_name:
            method_class = None
        else:
            method_class = self._ensure_class(class_name)
        return method_class, proc_name, operator

    def _ensure_class(self, class_name):
        declared_type = self._declared_types.get(class_name)
        if declared_type is not None:
            return declared_type
        # A class from a mangled name exists even if it is not declared
        class_type = data_types.ClassType(class_name, {})
        self._declared_types[class_name] = class_type
        return class_type

    @property
    def _current_char(self):
        return self._decl_str[self._pos]

    def _expect(self, c):
        if self._decl_str[self._pos] != c:
            raise Exception(
                "Expected {} but was: {}.".format(c, self._decl_str[self._pos]))
        self._pos += 1

    def _pop_char(self):
        c = self._current_char
        self._pos += 1
        return c

    def _try_pop_char(self, c):
        if self._current_char != c:
            return False
        self._pos += 1
        return True

    def _pop_qualified_identifier(self):
        identifiers = []
        while not self._try_pop_char("@"):
            identifiers.append(self._pop_identifier())
        return identifiers

    def _pop_identifier(self):
        if self._current_char.isdigit():
            return self._names[int(self._pop_char())]
        id_chars = []
        while not self._try_pop_char("@"):
            id_chars.append(self._pop_char())
        identifier = "".join(id_chars)
        self._names.append(identifier)
        return identifier

    def _pop_calling_convention(self):
        return self._calling_conventions[self._pop_char()]

    def _pop_modifier(self):
        return self._modifiers[self._pop_char()]

    def _pop_const_modifier(self):
        return self._const_modifiers[self._pop_char()]

    def _pop_operator(self):
        operator = self._operators[self._pop_char()]
        if isinstance(operator, dict):
            return operator[self._pop_char()]
        return operator

    def _pop_data_type(self, arg_types=None):
        data_type = self._data_types[self._pop_char()]
        if callable(data_type):
            return data_type(self, arg_types)
        return data_type

    def _pop_reference_type(self, arg_types):
        return self._pop_pointer_or_reference_type(
            arg_types, data_types.Reference)

    def _pop_pointer_type(self, arg_types):
        return self._pop_pointer_or_reference_type(
            arg_types, data_types.Pointer32)

    def _pop_pointer_or_reference_type(self, arg_types, data_type):
        const_modifier = self._pop_const_modifier()
        data_type = data_type(self._pop_data_type())
        if const_modifier is not None:
            data_type.add_qualifier(const_modifier)
        if arg_types is not None:
            arg_types.append(data_type)
        return data_type

    def _pop_struct_type(self, arg_types):
        return self._pop_class_type(arg_types)

    def _pop_class_type(self, arg_types):
        (class_name,) = self._pop_qualified_identifier()
        class_type = self._ensure_class(class_name)
        if arg_types is not None:
            arg_types.append(class_type)
        return class_type

    def _pop_enum_type(self, arg_types):
        self._expect("4")
        enum_names = self._pop_qualified_identifier()
        assert len(enum_names) == 2
        enum_name, namespace_name = enum_names
        namespace_type = self._ensure_class(namespace_name)
        enum_type = self._declared_types.get(enum_name)
        if enum_type is None:
            enum_type = data_types.make_named_type(
                data_types.Int32(), enum_name)
            self._declared_types[enum_name] = enum_type
        enum_type.set_namespace(namespace_type)
        if arg_types is not None:
            arg_types.append(enum_type)
        return enum_type

    _calling_conventions = {
        "A": CallingConvention.CDECL,
        "E": CallingConvention.THISCALL,
    }

    _modifiers = {
        "A": (True, False, False, "private"),
        "Q": (True, False, False, "public"),
        "S": (True, True, False, "public"),
        "U": (True, False, True, "public"),
        "Y": (False, False, False, None)
    }

    _const_modifiers = {
        "A": None,
        "B": "const",
    }

    _operators = {
        "0": _Operator(is_constructor=True),
        "1": _Operator(is_destructor=True),
        "4": _Operator("operator="),
        "5": _Operator("operator>>"),
        "6": _Operator("operator<<"),
        "8": _Operator("operator=="),
        "9": _Operator("operator!="),
        "D": _Operator("operator*"),
        "H": _Operator("operator+"),
        "K": _Operator("operator/"),
        "M": _Operator("operator<"),
        "O": _Operator("operator>"),
        "Y": _Operator("operator+="),
        "_": {
            "F": _Operator("default constructor closure"),
            "G": _Operator("scalar deleting destructor"),
        }
    }

    _data_types = {
        "0": lambda parser, arg_types: arg_types[0],
        "A": _pop_reference_type,
        "D": data_types.Char(),
        "E": data_types.UChar(),
        "F": data_types.Short(),
        "G": data_types.UShort(),
        "H": data_types.Int32(),
        "I": data_types.UInt32(),
        "J": data_types.Long32(),
        "K": data_types.make_named_type(data_types.UInt32(), "unsigned long"),
        "M": data_types.Float(),
        "N": data_types.Double(),
        "P": _pop_pointer_type,
        "U": _pop_struct_type,
        "V": _pop_class_type,
        "W": _pop_enum_type,
        "X": None,
    }
