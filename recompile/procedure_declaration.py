import re

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import operators

operator_regexp = re.compile(r'^operator\s*(?P<op>\S+)$')
# Name of parameters written without names, e.g. unused parameters
UNNAMED_PARAMETER = "__"


class ProcedureDeclaration:
    def __init__(
        self, proc_name, convention, method_class, parameters, return_arg,
        is_static=False, is_virtual=False, is_vararg=False, is_const=False,
        access="public",
    ):
        self._proc_name = proc_name
        self._convention = convention
        self._method_class = method_class
        self._return_arg = return_arg
        self._parameters = parameters
        self._is_static = is_static
        self._is_virtual = is_virtual
        self._is_vararg = is_vararg
        self._is_const = is_const
        self._access = access
        self._operator = self._get_operator()
        self._is_default_constructor_closure = (
            proc_name == "default constructor closure"
        )
        self._is_scalar_deleting_destructor = (
            proc_name == "scalar deleting destructor"
        )
        self._stack_variable = None

    def copy(self, parameters=None):
        if parameters is None:
            parameters = self._parameters
        return ProcedureDeclaration(
            self._proc_name,
            self._convention,
            self._method_class,
            parameters,
            self._return_arg,
            is_static=self._is_static,
            is_virtual=self._is_virtual,
            is_vararg=self._is_vararg,
            is_const=self._is_const,
            access=self._access,
        )


    @property
    def proc_name(self):
        return self._proc_name

    @property
    def convention(self):
        return self._convention

    @property
    def method_class(self):
        return self._method_class

    @property
    def return_type(self):
        if self._return_arg is None and self.is_constructor:
            return data_types.Reference(self.method_class)
        return self._return_arg

    @property
    def parameters(self):
        return list(self._parameters)

    @property
    def access(self):
        return self._access

    def set_access(self, access):
        self._access = access

    @property
    def is_static(self):
        return self._is_static

    @property
    def is_virtual(self):
        return self._is_virtual

    @property
    def is_instance_method(self):
        return not self._is_static and self._method_class is not None

    @property
    def is_const(self):
        return self._is_const

    @property
    def is_constructor(self):
        if self._method_class is None:
            return False
        return self._method_class.class_name == self._proc_name

    @property
    def is_destructor(self):
        return self._proc_name is not None and self._proc_name.startswith("~")

    @property
    def is_vararg(self):
        return self._is_vararg

    @property
    def is_default_constructor_closure(self):
        return self._is_default_constructor_closure

    @property
    def is_scalar_deleting_destructor(self):
        return self._is_scalar_deleting_destructor

    @property
    def stack_delta(self):
        if self._convention == CallingConvention.CDECL:
            return 0
        stack_delta = 0
        for parameter_type, parameter_name in self._parameters:
            stack_delta += parameter_type.size
            stack_delta = ((stack_delta + 3) // 4) * 4
        if isinstance(self._return_arg, data_types.ClassType):
            stack_delta += data_types.Pointer32().size
        return stack_delta

    @property
    def stack_variables(self):
        if self._stack_variable is None:
            self._stack_variable = self._get_stack_variables()
        return self._stack_variable

    @property
    def operator(self):
        return self._operator

    def _get_operator(self):
        if self._proc_name is None:
            return None
        match = operator_regexp.search(self._proc_name)
        if match:
            # Operators without expressions, e.g. operator[], are methods
            return operators.get(match.group("op"))
        return None

    def _get_stack_variables(self):
        param_ids = list(self.get_parameters_ids().values())
        if self.is_instance_method:
            param_ids = param_ids[1:]
        offset = 8
        stack_dict = {}
        if isinstance(self._return_arg, data_types.ClassType):
            param_ids.insert(
                0,
                expressions.Identifier(
                    data_types.Pointer32(self._return_arg), "__result"))
        for param_id in param_ids:
            stack_dict[offset] = param_id
            offset += param_id.data_type.size
            offset = ((offset + 3) // 4) * 4
        return stack_dict

    def change_return_type(self, return_type):
        self._return_arg = return_type
        self._stack_variable = None

    def get_parameters_ids(self, expected_args_types=False):
        make_id = expressions.Identifier
        param_dict = {}
        if self.is_instance_method:
            param_name = "this"
            reference_to = self._reference_to_this(expected_args_types)
            param_type = reference_to(self._method_class)
            param_dict[param_name] = make_id(param_type, param_name)
        param_index = 0
        for param_type, param_name in self._parameters:
            param_index += 1
            param_name = _make_parameter_name(param_name, param_index)
            param_dict[param_name] = make_id(param_type, param_name)
        return param_dict

    def _reference_to_this(self, expected_args_types):
        if expected_args_types and self.operator is not None:
            return data_types.Reference
        return data_types.Pointer32

    def get_declaration(self, is_definition=False):
        parameters = []
        param_index = 0
        for parameter_type, parameter_name in self._parameters:
            param_index += 1
            if parameter_name == UNNAMED_PARAMETER:
                parameter_name = None
            else:
                parameter_name = _make_parameter_name(
                    parameter_name, param_index)
            parameter = parameter_type.make_variable_declaration(
                parameter_name, self._method_class
            )
            parameters.append(parameter)
        static_modifier = ""
        if self._is_static and not is_definition:
            static_modifier = "static "
        virtual_modifier = ""
        if self._is_virtual and not is_definition:
            virtual_modifier = "virtual "
        proc_name = self._proc_name
        if self._operator is not None:
            proc_name = "operator {}".format(self._operator.value)
        if is_definition and self._method_class is not None:
            proc_name = "{}::{}".format(
                self._method_class.class_name, proc_name
            )
        return_arg = self._get_return_type_name()
        sep = "" if not return_arg or return_arg[-1] in {"*", "&"} else " "
        calling_convention = ""
        if self._convention == CallingConvention.STDCALL:
            calling_convention = "__stdcall "
        const = ""
        if self._is_const:
            const = " const"
        return "{}{}{}{}{}{}({}){}".format(
            static_modifier,
            virtual_modifier,
            return_arg,
            sep,
            calling_convention,
            proc_name,
            ", ".join(parameters),
            const,
        )

    def _get_return_type_name(self):
        if self.is_constructor or self.is_destructor:
            return ""
        if self._return_arg is None:
            return "void"
        decl = self._return_arg.make_variable_declaration("")
        return decl.strip()


def _make_parameter_name(parameter_name, parameter_index):
    if parameter_name is not None and parameter_name != UNNAMED_PARAMETER:
        return parameter_name
    return "arg_{}".format(parameter_index)
