import struct

import expressions
import data_types
from expressions.do_pointer_dereference import do_pointer_dereference


def transform_reinterpret(data_type, expression, analysis, **kwargs):
    result = _transform_string_constant(data_type, expression, **kwargs)
    if result is not None:
        return result
    result = _transform_float_constant(data_type, expression, **kwargs)
    if result is not None:
        return result
    result = _transform_to_static_cast(data_type, expression)
    if result is not None:
        return result
    result = _transform_to_first_field(data_type, expression)
    if result is not None:
        return result
    analysis.process_reinterpret(data_type, expression)
    return expressions.do_reinterpret(data_type, expression)


def _transform_string_constant(data_type, expression, declarations, **kwargs):
    if not isinstance(data_type, data_types.Pointer32):
        return None
    if not isinstance(data_type.pointee, data_types.Char):
        return None
    global_variable = expression
    if not isinstance(global_variable, expressions.intermediate.Global):
        return None
    string_const = declarations.string_constants.get(global_variable.address)
    if string_const is None:
        return None
    return expressions.StringConstant(string_const)


def _transform_float_constant(data_type, expression, declarations, **kwargs):
    value = get_float_constant(data_type, expression, declarations)
    if value is None:
        return None
    return expressions.Constant(data_type, value)


def get_float_constant(data_type, expression, declarations):
    """Return value of read only float or double constant or None."""
    unpack_format = _float_formats.get(type(data_type))
    if unpack_format is None:
        return None
    if not isinstance(expression, expressions.intermediate.Access):
        return None
    global_variable = expression.expression
    if not isinstance(global_variable, expressions.intermediate.Global):
        return None
    if expression.size != data_type.size:
        return None
    data = declarations.read_only_data.get_bytes(
        global_variable.address + expression.offset, data_type.size)
    if data is None:
        return None
    (value, ) = struct.unpack(unpack_format, data)
    if value != value or value in (float("inf"), float("-inf")):
        return None
    if isinstance(data_type, data_types.Float):
        value = _shortest_float(value)
    return value


def _shortest_float(value):
    # Shortest decimal representation of 32-bit float
    for precision in range(1, 10):
        shortest = float("{:.{}g}".format(value, precision))
        if struct.unpack("<f", struct.pack("<f", shortest))[0] == value:
            return shortest
    return value


_float_formats = {
    data_types.Float: "<f",
    data_types.Double: "<d",
}


def _transform_to_static_cast(data_type, expression):
    conv = _static_cast_pairs.get((type(expression.data_type), type(data_type)))
    if conv is None:
        return None
    return expressions.StaticCast(data_type, expression)


_static_cast_pairs = {
    (data_types.Long32, data_types.UInt32): True,
    (data_types.UInt32, data_types.Long32): True,
    (data_types.SizeT, data_types.UInt32): True,
    (data_types.UInt32, data_types.SizeT): True,
}


def _transform_to_first_field(data_type, expression):
    """Transform cast of pointer to class to pointer to its first field."""
    if not isinstance(data_type, data_types.Pointer32):
        return None
    pointee = data_type.pointee
    if pointee is None:
        return None
    if not isinstance(expression.data_type, data_types.Pointer32):
        return None
    if not isinstance(expression.data_type.pointee, data_types.ClassType):
        return None
    if pointee.size >= expression.data_type.pointee.size:
        return None
    try:
        field = do_pointer_dereference(expression, 0, pointee.size)
    except Exception:
        return None
    if field is None or not data_types.are_same(field.data_type, pointee):
        return None
    return expressions.AddressOf(field)
