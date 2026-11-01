import expressions
import data_types


def transform_reinterpret(data_type, expression, analysis, **kwargs):
    result = _transform_string_constant(data_type, expression, **kwargs)
    if result is not None:
        return result
    result = _transform_to_static_cast(data_type, expression)
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
    (data_types.Int32, data_types.UInt32): True,
    (data_types.UInt32, data_types.Int32): True,
}
