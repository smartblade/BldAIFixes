import data_types
import expressions
from expressions.operator import Operator
from get_procedure_declaration_at import get_procedure_declaration_at
from calling_convention import CallingConvention
from patterns.validate_procedure_declaration import \
    validate_procedure_declaration

from .apply_parameter_characteristics import apply_parameter_characteristics
from .call_characteristics import get_call_characteristics
from .convert_sizeof_arguments import convert_sizeof_arguments
from .explicit_arg_cast import explicit_arg_cast
from .narrow_constant import narrow_constant


def transform_procedure_call(
    pc, analysis, declarations, file_declarations, call_args_matcher, **kwargs
):
    pc, proc_decl = _resolve_virtual_call(pc)
    if proc_decl is None:
        proc_decl = _get_callee_declaration(pc, declarations)
    pc = call_args_matcher.match_args(pc, proc_decl)
    if proc_decl is None:
        return pc
    assert pc.proc_decl is not None
    call_characteristics = get_call_characteristics(declarations, pc)
    result = _convert_struct_return_implicit_arg(
        pc, analysis, file_declarations, call_characteristics, proc_decl)
    if result is not None:
        return result
    return_type = pc.proc_decl.return_type
    pc = _convert_procedure_call_arguments(
        pc, analysis, file_declarations, call_characteristics, proc_decl)
    return _convert_to_return_type(pc, return_type)


def _convert_procedure_call_arguments(
    pc, analysis, file_declarations, call_characteristics, proc_decl
):
    pc = pc.copy(arguments=_merge_split_arguments(pc.arguments, proc_decl))
    arguments = _convert_arguments_to_parameters_types(
        pc, analysis, file_declarations, call_characteristics, proc_decl)
    arguments = convert_sizeof_arguments(arguments, proc_decl)
    return pc.copy(
        name=proc_decl.proc_name, proc_decl=proc_decl, arguments=arguments)


def _resolve_virtual_call(pc):
    """Resolve 'obj->(vtbl(obj)[index])(args)' to 'obj->Method(args)'."""
    callee = pc.callee_expression
    if not pc.is_method or not isinstance(
        callee, expressions.intermediate.Access
    ):
        return pc, None
    vtbl = callee.expression
    if not isinstance(vtbl, expressions.intermediate.Access):
        return pc, None
    if vtbl.offset != 0 or vtbl.size != 4 or callee.size != 4:
        return pc, None
    obj = vtbl.expression
    if obj.emit_code() != pc.arguments[0].emit_code():
        return pc, None
    if not isinstance(obj.data_type, data_types.Pointer32):
        return pc, None
    class_type = obj.data_type.pointee
    if not isinstance(class_type, data_types.ClassType):
        return pc, None
    index, rest = divmod(callee.offset, 4)
    methods = class_type.virtual_methods
    if rest != 0 or index >= len(methods):
        return pc, None
    method = methods[index]
    # Slot of virtual destructor is scalar deleting destructor
    if method.is_destructor:
        return pc, None
    # Declared virtual methods may not match the actual table
    if method.stack_delta != pc.proc_decl.stack_delta:
        return pc, None
    return pc.copy(callee=None, name=method.proc_name), method


def _get_callee_declaration(pc, declarations):
    if pc.callee_expression is not None:
        assert pc.callee_address is None
        return _get_declaration_from_callee_expression(pc.callee_expression)
    if pc.callee_address is None:
        return declarations.external_procedures.get(pc.name)
    return get_procedure_declaration_at(declarations, pc.callee_address)


def _get_declaration_from_callee_expression(e):
    function = e.data_type
    if isinstance(function, data_types.Unknown32):
        return None
    assert isinstance(function, data_types.Function)
    return function.proc_decl


def _merge_split_arguments(arguments, proc_decl):
    """Merge halves of 8-byte arguments pushed from stack variables."""
    parameters = list(proc_decl.get_parameters_ids().values())
    if len(arguments) <= len(parameters):
        return arguments
    new_arguments = []
    i = 0
    for parameter in parameters:
        if i >= len(arguments):
            return arguments
        low = arguments[i]
        high = arguments[i + 1] if i + 1 < len(arguments) else None
        if (
            parameter.data_type.size == 8 and
            isinstance(low, expressions.intermediate.Stackvar) and
            isinstance(high, expressions.intermediate.Stackvar) and
            low.size == 4 and high.size == 4 and
            high.offset == low.offset + 4
        ):
            new_arguments.append(
                expressions.intermediate.Stackvar(low.offset, 8))
            i += 2
        else:
            new_arguments.append(low)
            i += 1
    if i != len(arguments):
        return arguments
    return new_arguments


def _convert_arguments_to_parameters_types(
    pc, analysis, file_declarations, call_characteristics, proc_decl
):
    if (
        len(pc.arguments) != len(proc_decl.get_parameters_ids()) and
        (
            not proc_decl.is_vararg or
            len(pc.arguments) < len(proc_decl.get_parameters_ids())
        )
    ):
        raise Exception(
            "Expected to be {} arguments at {} but was: {}".format(
                len(pc.arguments),
                proc_decl.proc_name,
                len(proc_decl.get_parameters_ids()),
            )
        )
    validate_procedure_declaration(
        proc_decl,
        stack_delta=pc.proc_decl.stack_delta,
        is_thiscall=pc.proc_decl.convention == CallingConvention.THISCALL)
    new_arguments = []
    parameters = list(
        proc_decl.get_parameters_ids(expected_args_types=True).values())
    for i, argument in enumerate(pc.arguments):
        parameter = parameters[i] if i < len(parameters) else None
        new_argument = _convert_argument_to_parameters_type(
            argument, parameter, proc_decl)
        new_argument = apply_parameter_characteristics(
            new_argument,
            file_declarations,
            call_characteristics.parameters[i]
        ) or new_argument
        new_arguments.append(new_argument)
    analysis.process_arguments(new_arguments, call_characteristics)
    return new_arguments


def _convert_argument_to_parameters_type(argument, parameter, proc_decl):
    if parameter is None:
        return argument
    c = narrow_constant(argument, parameter.data_type)
    if c is not None:
        return c
    new_argument = expressions.do_reinterpret(parameter.data_type, argument)
    new_argument = explicit_arg_cast(
        proc_decl, new_argument, parameter.data_type) or new_argument
    return new_argument


def _convert_struct_return_implicit_arg(
    pc, analysis, file_declarations, call_characteristics, proc_decl
):
    if not isinstance(proc_decl.return_type, data_types.ClassType):
        return None
    # Check if it was already transformed
    if data_types.are_same(proc_decl.return_type, pc.proc_decl.return_type):
        return None
    assert (
        pc.proc_decl.return_type is None or
        isinstance(pc.proc_decl.return_type, data_types.Unknown32)
    )
    this_arg = None
    new_arguments = pc.arguments
    if pc.is_method:
        this_arg = new_arguments[0]
        new_arguments = new_arguments[1:]
    return_arg = new_arguments[0]
    return_arg = expressions.do_reinterpret(
        data_types.Pointer32(proc_decl.return_type), return_arg)
    new_arguments = new_arguments[1:]
    if this_arg is not None:
        new_arguments.insert(0, this_arg)
    pc = pc.copy(arguments=new_arguments)
    pc = _convert_procedure_call_arguments(
        pc, analysis, file_declarations, call_characteristics, proc_decl)
    dst = expressions.do_dereference(return_arg)
    if isinstance(dst.data_type, data_types.ClassType):
        dst = expressions.MakeReference(dst)
    return expressions.Bin(Operator.ASS, dst, pc)


def _convert_to_return_type(pc, return_type):
    if return_type is None:
        return pc
    if data_types.are_compatible(pc.data_type, return_type):
        return pc
    if (
        isinstance(return_type, data_types.Unknown32) and
        pc.data_type.is_any_int and pc.data_type.size == 1
    ):
        return expressions.intermediate.TrashExtend(return_type, pc)
    if (
        isinstance(return_type, data_types.Double) and
        isinstance(pc.data_type, data_types.Float)
    ):
        # Floating point values are returned in FPU register
        return expressions.do_static_cast(return_type, pc)
    raise Exception(
        'Incompatible return type of {} procedure: {}, can\'t be converted to '
        '{}'.format(pc.name, pc.data_type, return_type)
    )
