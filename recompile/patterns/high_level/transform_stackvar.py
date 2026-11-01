from .struct_variable_field import struct_variable_field


def transform_stackvar(offset, size, stack_vars, analysis, **kwargs):
    variable = stack_vars.get(offset)
    if variable is not None and variable.data_type.size == size:
        return variable
    field = struct_variable_field(stack_vars, offset, size)
    if field is not None:
        return field
    analysis.process_stackvar(offset, size)
    return None
