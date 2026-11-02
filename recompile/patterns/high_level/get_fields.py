def get_fields(class_type):
    fields = []
    cur_field_and_offset = _get_type_at(class_type, 0)
    if cur_field_and_offset is None:
        return fields
    while cur_field_and_offset is not None:
        cur_field_offset, cur_field = cur_field_and_offset
        fields.append(cur_field)
        cur_field_type, cur_field_name = cur_field
        size = cur_field_type.size
        # Parent without fields has the table of virtual methods only
        if (
            cur_field_name is None and size == 0 and
            cur_field_type.has_virtual_methods
        ):
            size = 4
        if size == 0:
            cur_field_offset += 1
        else:
            cur_field_offset += size
        cur_field_and_offset = _get_type_at(class_type, cur_field_offset)
    return fields


def _get_type_at(class_type, offset):
    if offset == 0 and class_type.parent is not None:
        return 0, (class_type.parent, None)
    field_offset = class_type.find_nearest_field_offset(offset)
    # Skip virtual methods table
    if field_offset is None and offset == 0:
        offset += 4
        field_offset = class_type.find_nearest_field_offset(offset)
    if field_offset is None:
        return None
    return field_offset, class_type.get_field_by_offset(field_offset)
