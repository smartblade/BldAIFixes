import data_types
import expressions


def do_pointer_dereference(expression, offset, size):
    if isinstance(expression.data_type, data_types.Unknown32):
        return None
    if (
        isinstance(expression.data_type, data_types.AnyInt) and
        expression.data_type.size == data_types.Pointer32().size
    ):
        return None
    if isinstance(expression.data_type, data_types.Reference):
        expression = expressions.AddressOf(expression)
    if not isinstance(expression.data_type, data_types.Pointer32):
        raise Exception(
            "Data type of {} expected to be pointer but was: {}.".format(
                expression, expression.data_type))
    pointee = expression.data_type.pointee
    if isinstance(pointee, data_types.ClassType):
        field_offset = pointee.find_nearest_field_offset(offset)
        if field_offset is None:
            return None
        data_type, field_name = pointee.get_field_by_offset(field_offset)
        field_access = expressions.FieldAccess(expression, field_name)
        if field_offset != offset or size is not None and data_type.size > size:
            return do_pointer_dereference(
                expressions.AddressOf(field_access),
                offset - field_offset,
                size,
            )
        if size is not None and data_type.size != size:
            raise Exception(
                "Data type size expected to be {} but was: {}.".format(
                    size, data_type.size))
        return field_access
    if isinstance(pointee, data_types.Array) and 0 < offset < pointee.size:
        return _dereference_array_element(expression, pointee, offset, size)
    if isinstance(pointee, data_types.Array) and offset == 0:
        data_type = pointee.element_type
        if size is not None and data_type.size != size:
            raise Exception(
                "Data type size expected to be {} but was: {}.".format(
                    size, data_type.size))
        if size is None:
            if isinstance(expression, expressions.AddressOf):
                return expressions.do_dereference(expression)
        else:
            array_access = expressions.ArrayAccess(
                expressions.do_dereference(expression),
                expressions.Constant(data_types.Int32(), offset),
            )
            return array_access
    if isinstance(
        pointee, (
            data_types.Char, data_types.UChar,
            data_types.Int32, data_types.UInt32,
            data_types.Pointer32,
        )
    ):
        dereference = expressions.do_dereference(expression)
        if size is not None and pointee.size != size:
            if pointee.is_any_int and size < pointee.size:
                return expressions.do_static_cast(
                    data_types.AnyInt(size), dereference)
            raise Exception(
                "Data type size expected to be {} but was: {}.".format(
                    size, pointee.size))
        if offset != 0:
            raise Exception(
                "Data access offset expected to be {} but was: {}.".format(
                    0, offset))
        return dereference
    return None


def _dereference_array_element(expression, array_type, offset, size):
    """Access to data at the offset inside an element of the array."""
    element_type = array_type.element_type
    index, element_offset = divmod(offset, element_type.size)
    if size is not None and element_offset + size > element_type.size:
        # Access to several elements
        return None
    array_access = expressions.ArrayAccess(
        expressions.do_dereference(expression),
        expressions.Constant(data_types.Int32(), index),
    )
    if element_offset == 0 and (size is None or element_type.size == size):
        return array_access
    return do_pointer_dereference(
        expressions.AddressOf(array_access), element_offset, size)
