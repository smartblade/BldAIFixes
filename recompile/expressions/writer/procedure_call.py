import data_types
import expressions

from .strip_implicit_conversion import strip_implicit_conversion


def write_procedure_call(
    proc_decl, is_method, proc_name, callee, arguments
):
    arguments = _strip_implicit_conversions(proc_decl, arguments)
    operator = proc_decl.operator if proc_decl is not None else None
    if operator is not None and len(arguments) == 2:
        assert callee is None
        return "{} {} {}".format(
            arguments[0].emit_code(),
            operator.value,
            arguments[1].emit_code(),
        )
    if is_method:
        call = _method_access_code(arguments[0], proc_decl, callee, proc_name)
        arguments = arguments[1:]
    else:
        if proc_decl is not None and proc_decl.is_static:
            assert callee is None
            call = "{}::{}".format(
                proc_decl.method_class.class_name, proc_name)
        else:
            call = _callee_code(callee, proc_name)
    return "{}({})".format(
        call, ", ".join(map(lambda a: a.emit_code(), arguments))
    )


def _is_obj_initialization(obj, proc_decl):
    if proc_decl is None:
        return False
    if not proc_decl.is_constructor:
        return False
    if not isinstance(obj, expressions.AddressOf):
        return False
    identifier = obj.expression
    if not isinstance(identifier, expressions.Identifier):
        return False
    return identifier.is_implicit


def _method_access_code(obj, proc_decl, callee, proc_name):
    if callee is not None:
        method_code = "({})".format(callee.emit_code())
    else:
        method_code = proc_name
    if _is_obj_initialization(obj, proc_decl):
        return method_code
    if isinstance(obj.data_type, data_types.Reference):
        obj = expressions.AddressOf(obj)
    return expressions.FieldAccess(obj, method_code).emit_code()


def _callee_code(callee, proc_name):
    if callee is not None:
        return callee.emit_code()
    return proc_name


def _strip_implicit_conversions(proc_decl, arguments):
    if proc_decl is None:
        return arguments
    parameters = list(
        proc_decl.get_parameters_ids(expected_args_types=True).values())
    new_arguments = []
    for i, argument in enumerate(arguments):
        parameter = parameters[i] if i < len(parameters) else None
        new_argument = _strip_implicit_conversions_from_arg(parameter, argument)
        new_arguments.append(new_argument or argument)
    return new_arguments


def _strip_implicit_conversions_from_arg(parameter, argument):
    if parameter is None:
        return None
    parameter_type = parameter.data_type
    if not data_types.are_same(argument.data_type, parameter_type):
        return None
    return strip_implicit_conversion(argument)
