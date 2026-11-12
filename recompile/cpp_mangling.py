"""Mangling of procedure declarations by the rules of Visual C++ 6.0."""

from calling_convention import CallingConvention
import data_types
from data_types.named_type import NamedType

# Codes of operators and special procedures after '?'
_operator_codes = {
    "operator=": "4",
    "operator>>": "5",
    "operator<<": "6",
    "operator!": "7",
    "operator==": "8",
    "operator!=": "9",
    "operator[]": "A",
    "operator->": "C",
    "operator*": "D",
    "operator++": "E",
    "operator--": "F",
    "operator-": "G",
    "operator+": "H",
    "operator&": "I",
    "operator/": "K",
    "operator%": "L",
    "operator<": "M",
    "operator<=": "N",
    "operator>": "O",
    "operator>=": "P",
    "operator()": "R",
    "operator~": "S",
    "operator^": "T",
    "operator|": "U",
    "operator&&": "V",
    "operator||": "W",
    "operator*=": "X",
    "operator+=": "Y",
    "operator-=": "Z",
    "operator/=": "_0",
    "operator%=": "_1",
    "operator>>=": "_2",
    "operator<<=": "_3",
    "operator&=": "_4",
    "operator|=": "_5",
    "operator^=": "_6",
    "default constructor closure": "_F",
    "scalar deleting destructor": "_G",
}

# Codes of methods: (access, is_static, is_virtual) -> code
_method_codes = {
    ("private", False, False): "A",
    ("private", True, False): "C",
    ("private", False, True): "E",
    ("protected", False, False): "I",
    ("protected", True, False): "K",
    ("protected", False, True): "M",
    ("public", False, False): "Q",
    ("public", True, False): "S",
    ("public", False, True): "U",
}

_calling_convention_codes = {
    CallingConvention.CDECL: "A",
    CallingConvention.THISCALL: "E",
    CallingConvention.STDCALL: "G",
    CallingConvention.FASTCALL: "I",
}

# Types without names
_simple_type_codes = [
    (data_types.UChar, "E"),
    (data_types.Char, "D"),
    (data_types.UShort, "G"),
    (data_types.Short, "F"),
    (data_types.UInt32, "I"),
    (data_types.Int32, "H"),
    (data_types.Long32, "J"),
    (data_types.Float, "M"),
    (data_types.Double, "N"),
    (data_types.Bool, "_N"),
]

# Types encoded by the names of their typedefs
_named_type_codes = {
    "unsigned long": "K",
    "long": "J",
    "bool": "_N",
}

# Back references to names and to types of parameters are digits
_max_back_references = 10


def mangle_cpp(proc_decl):
    """Return the name of a procedure declaration mangled by Visual C++
    6.0, e.g. '?Seek@B_IDataFile@@QAEJJH@Z'."""
    return _CppMangler().mangle(proc_decl)


class _CppMangler:
    def __init__(self):
        self._names = []
        self._arg_types = []

    def mangle(self, proc_decl):
        parts = ["?", self._mangle_qualified_name(proc_decl)]
        method_class = proc_decl.method_class
        if method_class is None:
            parts.append("Y")
        else:
            key = (
                proc_decl.access, proc_decl.is_static, proc_decl.is_virtual)
            parts.append(_method_codes[key])
            if not proc_decl.is_static:
                parts.append("B" if proc_decl.is_const else "A")
        parts.append(_calling_convention_codes[proc_decl.convention])
        if proc_decl.is_constructor or proc_decl.is_destructor:
            parts.append("@")
        else:
            parts.append(self._mangle_return_type(proc_decl))
        parts.append(self._mangle_parameters(proc_decl))
        parts.append("Z")
        return "".join(parts)

    def _mangle_qualified_name(self, proc_decl):
        method_class = proc_decl.method_class
        proc_name = proc_decl.proc_name
        if proc_decl.is_constructor:
            parts = ["?0"]
        elif proc_decl.is_destructor:
            parts = ["?1"]
        else:
            if proc_name.startswith("operator"):
                # 'operator >>' of sources is 'operator>>' of demangling
                proc_name = proc_name.replace(" ", "")
            code = _operator_codes.get(proc_name)
            if code is not None:
                parts = ["?" + code]
            else:
                parts = [self._mangle_name(proc_name)]
        if method_class is not None:
            parts.append(self._mangle_name(method_class.class_name))
        parts.append("@")
        return "".join(parts)

    def _mangle_name(self, name):
        if name in self._names:
            return str(self._names.index(name))
        if len(self._names) < _max_back_references:
            self._names.append(name)
        return name + "@"

    def _mangle_return_type(self, proc_decl):
        return_type = proc_decl.return_type
        if return_type is None:
            return "X"
        if (
            isinstance(return_type, data_types.ClassType) and
            return_type.class_name not in _named_type_codes
        ):
            # Classes returned by value are prefixed with their qualifiers
            return _class_return_prefix(return_type) + self._mangle_type(
                return_type)
        return self._mangle_type(return_type)

    def _mangle_parameters(self, proc_decl):
        parameters = [data_type for data_type, _ in proc_decl.parameters]
        if not parameters and not proc_decl.is_vararg:
            return "X"
        parts = [self._mangle_argument_type(t) for t in parameters]
        # '@' ends parameters, 'Z' ends them with '...'
        parts.append("Z" if proc_decl.is_vararg else "@")
        return "".join(parts)

    def _mangle_argument_type(self, data_type):
        key = _type_key(data_type)
        if key in self._arg_types:
            return str(self._arg_types.index(key))
        encoded = self._mangle_type(data_type)
        if len(encoded) > 1 and len(self._arg_types) < _max_back_references:
            self._arg_types.append(key)
        return encoded

    def _mangle_type(self, data_type):
        if data_type is None:
            return "X"
        if isinstance(data_type, data_types.Pointer32):
            return self._mangle_indirection(
                "Q" if _has_right_const(data_type) else "P",
                data_type, data_type.pointee)
        if isinstance(data_type, data_types.Reference):
            return self._mangle_indirection(
                "A", data_type, data_type.referent)
        if isinstance(data_type, NamedType):
            return self._mangle_named_type(data_type)
        if isinstance(data_type, data_types.ClassType):
            if data_type.class_name in _named_type_codes:
                return _named_type_codes[data_type.class_name]
            code = "U" if data_type.is_struct else "V"
            return "{}{}@".format(
                code, self._mangle_namespaced_name(data_type))
        for type_class, code in _simple_type_codes:
            if isinstance(data_type, type_class):
                return code
        raise Exception("Cannot mangle type: {}".format(data_type))

    def _mangle_indirection(self, code, data_type, target):
        is_const = (
            "const" in data_type.qualifiers or
            target is not None and "const" in target.qualifiers
        )
        return "{}{}{}".format(
            code, "B" if is_const else "A", self._mangle_type(target))

    def _mangle_named_type(self, data_type):
        type_name = data_type.get_type_name()
        if type_name in _named_type_codes:
            return _named_type_codes[type_name]
        if data_type._namespace_type is not None:
            # Enums are declared in classes
            return "W4{}@".format(self._mangle_namespaced_name(data_type))
        # Typedefs are mangled as their types
        return self._mangle_type(data_type.referenced_type)

    def _mangle_namespaced_name(self, data_type):
        parts = [self._mangle_type_name(data_type)]
        namespace_type = data_type._namespace_type
        while namespace_type is not None:
            parts.append(self._mangle_name(namespace_type.get_type_name()))
            namespace_type = namespace_type._namespace_type
        return "".join(parts)


    def _mangle_type_name(self, data_type):
        template_arguments = getattr(data_type, "template_arguments", None)
        if template_arguments is None:
            return self._mangle_name(data_type.get_type_name())
        # Arguments of a template have their own back references, the
        # instance of the template is one name
        arguments_mangler = _CppMangler()
        template_id = "?${}@{}@".format(
            arguments_mangler._mangle_name(data_type.template_name)[:-1],
            "".join(
                arguments_mangler._mangle_argument_type(argument)
                for argument in template_arguments))
        if template_id in self._names:
            return str(self._names.index(template_id))
        if len(self._names) < _max_back_references:
            self._names.append(template_id)
        return template_id


def _has_right_const(data_type):
    return "const" in data_type._right_qualifiers


def _class_return_prefix(class_type):
    if "const" in class_type.qualifiers:
        return "?B"
    return "?A"


def _type_key(data_type):
    """Types of parameters are compared by their full mangled names."""
    return _CppMangler()._mangle_type(data_type)
