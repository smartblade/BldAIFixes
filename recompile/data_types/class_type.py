import bisect

from data_types.data_type import DataType


class ClassType(DataType):
    def __init__(self, class_name, fields):
        super().__init__()
        self._class_name = class_name
        self._fields = fields
        self._methods = []
        self._parent = None
        self._fields_sorted = True
        self._sorted_offsets = None

    def __repr__(self):
        return "class {}".format(self._class_name)

    @property
    def class_name(self):
        return self._class_name

    def rename(self, new_name):
        return self.__class__(new_name, self._fields)

    @property
    def size(self):
        size = 0
        for offset, (field_type, field_name) in self._fields.items():
            if offset + field_type.size > size:
                size = offset + field_type.size
        return size

    @property
    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def add_method(self, method):
        self._methods.append(method)

    def find_method(self, method_name):
        found_method = None
        num_methods = 0
        for method in self._methods:
            if method.proc_name == method_name:
                found_method = method
                num_methods += 1
        if num_methods > 1:
            raise Exception(
                "More than 1 methods found: {}.".format(method_name))
        return found_method

    @property
    def virtual_methods(self):
        """Virtual methods in order of the virtual methods table."""
        if self._parent is not None:
            methods = self._parent.virtual_methods
        else:
            methods = []
        for method in self._methods:
            if not method.is_virtual:
                continue
            for index, base_method in enumerate(methods):
                if _is_override(method, base_method):
                    methods[index] = method
                    break
            else:
                methods.append(method)
        return methods

    @property
    def has_virtual_methods(self):
        for method in self._methods:
            if method.is_virtual:
                return True
        if self._parent is not None:
            return self._parent.has_virtual_methods
        return False

    def get_field_by_offset(self, offset):
        if offset not in self._fields and self._parent is not None:
            return self._parent.get_field_by_offset(offset)
        return self._fields[offset]

    def find_nearest_field_offset(self, offset):
        if offset in self._fields:
            return offset
        self._sort_fields()
        index = bisect.bisect_left(self._sorted_offsets, offset) - 1
        if index >= 0:
            found_offset = self._sorted_offsets[index]
            field_type, field_name = self._fields[found_offset]
            if found_offset < offset < found_offset + field_type.size:
                return found_offset
        if self._parent is not None:
            return self._parent.find_nearest_field_offset(offset)
        return None

    def find_data_type_by_field(self, field_name):
        for field_type, name in self._fields.values():
            if name == field_name:
                return field_type
        if self._parent is not None:
            return self._parent.find_data_type_by_field(field_name)
        raise Exception(
            "Field {} was not found at {}.".format(field_name, self)
        )

    def get_type_name(self):
        return self._class_name

    def _sort_fields(self):
        if self._fields_sorted:
            if self._sorted_offsets is None:
                self._sorted_offsets = list(sorted(self._fields.keys()))
            return
        self._fields = dict(sorted(self._fields.items()))
        self._fields_sorted = True
        self._sorted_offsets = list(self._fields.keys())


def _is_override(method, base_method):
    if method.is_destructor and base_method.is_destructor:
        return True
    return method.proc_name == base_method.proc_name
