import expressions

from .struct_variable_field import struct_variable_field


def transform_local(local, stack_vars, analysis, **kwargs):
    variable = stack_vars.get(local.offset)
    if variable is not None:
        return expressions.AddressOf(variable)
    field = struct_variable_field(stack_vars, local.offset, None)
    if field is not None:
        return expressions.AddressOf(field)
    analysis.process_local(local)
    return None
