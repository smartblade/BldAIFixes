import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
from expressions.operator import Operator


def transform_arrptr(base, scale, index, offset, **kwargs):
    row = _transform_row_address(base)
    if row is not None:
        base = row
    e = _transform_field_array_element(
        base, *_extract_scale(scale, index), offset)
    if e is not None:
        return e
    e = _transform_array_element(base, scale, index, offset)
    if e is not None:
        return e
    e = _transform_pointer_element(base, scale, index, offset)
    if e is not None:
        return e
    if scale != 1:
        return None
    if offset < 0:
        return None
    e = do_pointer_dereference(base, 0, None)
    if e is None:
        return None
    if isinstance(e.data_type, data_types.Array):
        element_type = e.data_type.element_type
    else:
        e = base
        element_type = e.data_type.pointee
    if element_type.size != 1:
        return None
    if offset > 0:
        index = expressions.Bin(
            Operator.ADD, index, expressions.Constant(index.data_type, offset))
    return expressions.AddressOf(expressions.ArrayAccess(e, index))


def _transform_field_array_element(base, scale, index, offset):
    """Transform address of element of array field: &base->field[index]."""
    data_type = base.data_type
    if isinstance(data_type, data_types.Pointer32):
        pointee = data_type.pointee
    elif isinstance(data_type, data_types.Reference):
        pointee = data_type.referent
    else:
        return None
    if not isinstance(pointee, data_types.ClassType) or offset < 0:
        return None
    field_offset = pointee.find_nearest_field_offset(offset)
    if field_offset is None:
        return None
    field_type, field_name = pointee.get_field_by_offset(field_offset)
    if not isinstance(field_type, data_types.Array):
        return None
    if field_type.element_type.size != scale:
        return None
    # Offset inside the element
    element_offset = offset - field_offset
    if element_offset >= scale:
        return None
    if isinstance(data_type, data_types.Reference):
        # Fields of a reference are accessed as fields of its address
        base = expressions.AddressOf(base)
    field = expressions.FieldAccess(base, field_name)
    element = expressions.ArrayAccess(field, index)
    if element_offset == 0:
        return expressions.AddressOf(element)
    e = do_pointer_dereference(
        expressions.AddressOf(element), element_offset, None)
    if e is None:
        return None
    return expressions.AddressOf(e)


def _transform_row_address(base):
    """Transform address of a row of an array field of several dimensions
    computed as integer: 'int(p) + 32 * i' -> '&p->m[i]'."""
    if not isinstance(base, expressions.Bin) or base.operator != Operator.ADD:
        return None
    for ptr, row_index in ((base.left, base.right), (base.right, base.left)):
        while isinstance(ptr, expressions.ReinterpretCast):
            ptr = ptr.expression
        scale, row_index = _extract_scale(1, row_index)
        if scale == 1:
            continue
        e = _transform_field_array_element(ptr, scale, row_index, 0)
        if e is not None:
            return e
    return None


def _transform_array_element(base, scale, index, offset):
    """Transform address of element of array addressed by its address:
    (&a, index) -> &a[index], e.g. &this->m[j][i] of a row &this->m[j]."""
    if offset != 0 or not isinstance(base, expressions.AddressOf):
        return None
    array = base.expression
    if not isinstance(array.data_type, data_types.Array):
        return None
    if array.data_type.element_type.size != scale:
        return None
    return expressions.AddressOf(expressions.ArrayAccess(array, index))


def _transform_pointer_element(base, scale, index, offset):
    """Transform address of element pointed by pointer: &base[index]."""
    if offset != 0 or scale == 1:
        return None
    if not isinstance(base.data_type, data_types.Pointer32):
        return None
    pointee = base.data_type.pointee
    if pointee is None or pointee.size != scale:
        return None
    if isinstance(pointee, data_types.UnknownTypes + (
        data_types.ClassType, data_types.Array
    )):
        return None
    return expressions.AddressOf(expressions.ArrayAccess(base, index))


def _extract_scale(scale, index):
    """Extract constant factor of index: (1, 8 * i) -> (8, i)."""
    if scale != 1:
        return scale, index
    if (
        not isinstance(index, expressions.Bin) or
        index.operator != Operator.MUL
    ):
        return scale, index
    for factor, rest in ((index.left, index.right), (index.right, index.left)):
        if (
            isinstance(factor, expressions.Constant) and
            isinstance(factor.value, int) and factor.value > 0
        ):
            return factor.value, rest
    return scale, index
