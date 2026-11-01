from data_types.array_type import Array
from data_types.pointer32 import Pointer32
from data_types.reference import Reference


def substitute_type(data_type, param, arg):
    """Substitute template parameter type 'param' with 'arg'."""
    if data_type is param:
        return arg
    if isinstance(data_type, Pointer32):
        if data_type.pointee is None:
            return data_type
        pointee = substitute_type(data_type.pointee, param, arg)
        if pointee is data_type.pointee:
            return data_type
        result = Pointer32(pointee)
    elif isinstance(data_type, Reference):
        referent = substitute_type(data_type.referent, param, arg)
        if referent is data_type.referent:
            return data_type
        result = Reference(referent)
    elif isinstance(data_type, Array):
        element_type = substitute_type(data_type.element_type, param, arg)
        if element_type is data_type.element_type:
            return data_type
        result = Array(element_type, data_type.length)
    else:
        return data_type
    result.set_qualifiers(list(data_type.qualifiers))
    return result
