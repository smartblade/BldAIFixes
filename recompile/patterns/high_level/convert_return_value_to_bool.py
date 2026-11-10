import data_types
import expressions
from expressions.operator import comparison


def convert_return_value_to_bool(proc_decl, characteristics, return_value):
    if characteristics.ret.is_not_boolean:
        return return_value
    if not characteristics.ret.is_boolean and not _is_boolean_return(proc_decl):
        return return_value
    if not isinstance(return_value, expressions.Constant):
        return return_value
    if not return_value.data_type.is_any_int:
        return return_value
    assert return_value.value == 0 or return_value.value == 1
    return expressions.Constant(data_types.Bool(), return_value.value)


def _is_boolean_return(proc_decl):
    if proc_decl is None:
        return False
    return proc_decl.operator in comparison
