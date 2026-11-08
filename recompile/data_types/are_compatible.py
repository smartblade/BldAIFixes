import data_types


def are_compatible(child, parent):
    if data_types.are_same(child, parent):
        return True
    if child.size != parent.size:
        return False
    if (
        isinstance(child, data_types.Pointer32) and
        isinstance(parent, data_types.Pointer32)
    ):
        if (
            isinstance(child.pointee, data_types.ClassType) and
            isinstance(parent.pointee, data_types.ClassType)
        ):
            return _is_instance_of(child.pointee, parent.pointee)
        if parent.pointee is None:
            return True
    if (
        child == data_types.NullptrType and
        isinstance(parent, data_types.Pointer32)
    ):
        return True
    if (
        not isinstance(child, data_types.UnknownTypes) and
        isinstance(parent, data_types.UnknownTypes)
    ):
        return True
    if (
        child.is_any_int and
        isinstance(parent, data_types.AnyInt)
    ):
        return True
    if (
        isinstance(child, data_types.Bool) and
        isinstance(parent, data_types.UChar)
    ):
        return True
    return False


def _is_instance_of(child_class, parent_class):
    while child_class.parent is not None:
        # Each instance of a class template is a separate class object
        if data_types.are_same(child_class.parent, parent_class):
            return True
        child_class = child_class.parent
    return False
