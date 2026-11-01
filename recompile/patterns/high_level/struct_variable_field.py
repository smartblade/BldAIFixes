import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference


def struct_variable_field(stack_vars, offset, size):
    """Return the field of a class variable at the stack offset or None."""
    for variable_offset, variable in stack_vars.items():
        if not isinstance(variable.data_type, data_types.ClassType):
            continue
        end = variable_offset + variable.data_type.size
        if not variable_offset <= offset < end:
            continue
        try:
            return do_pointer_dereference(
                expressions.AddressOf(variable), offset - variable_offset,
                size)
        except Exception:
            return None
    return None
