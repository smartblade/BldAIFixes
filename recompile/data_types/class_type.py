import bisect

from data_types.data_type import DataType


class ClassType(DataType):
    def __init__(self, class_name, fields):
        super().__init__()
        self._class_name = class_name
        self._fields = fields
        self._methods = []
        # Not virtual methods (e.g. inline methods) are kept apart: there may
        # be overloaded ones
        self._other_methods = []
        # Constructors are kept apart: there may be several of them
        self._constructors = []
        # Default values of parameters of constructors (C++ expressions)
        self._default_values = {}
        # Parents of multiple inheritance after the first one: (offset, type)
        self._other_parents = []
        self._parent = None
        self._fields_sorted = True
        self._sorted_offsets = None
        # Type of the parameter of class template
        self.template_param = None

    def __repr__(self):
        return "class {}".format(self._class_name)

    @property
    def class_name(self):
        return self._class_name

    def rename(self, new_name):
        return self.__class__(new_name, self._fields)

    def instantiate(self, new_name, arg):
        """Make class of template with parameter type substituted by arg."""
        return self.substitute(self.template_param, arg, new_name)

    def substitute(self, param, arg, new_name=None):
        """Make class with template parameter type substituted by arg."""
        from data_types.substitute_type import substitute_type
        if new_name is None:
            new_name = self._class_name.replace(
                "<{}>".format(param.get_type_name()),
                "<{}>".format(arg.get_type_name()))
        fields = dict(
            (offset, (substitute_type(t, param, arg), name))
            for offset, (t, name) in self._fields.items()
        )
        result = self.__class__(new_name, fields)
        if self._parent is not None:
            result.set_parent(self._parent.substitute(param, arg))
        for constructor in self._constructors:
            result.add_constructor(
                constructor, self._default_values.get(id(constructor)))
        return result

    def get_all_fields(self):
        """Fields of the class and its parents by offset."""
        fields = {}
        if self._parent is not None:
            fields.update(self._parent.get_all_fields())
        fields.update(self._fields)
        return fields

    @property
    def size(self):
        size = 0
        for offset, (field_type, field_name) in self._fields.items():
            if offset + field_type.size > size:
                size = offset + field_type.size
        return size

    @property
    def constructors(self):
        return list(self._constructors)

    def add_constructor(self, constructor, default_values=None):
        self._constructors.append(constructor)
        if default_values is not None:
            self._default_values[id(constructor)] = default_values

    def get_default_values(self, constructor):
        """Default values of parameters of constructor or None for each."""
        return self._default_values.get(id(constructor))

    @property
    def other_parents(self):
        return list(self._other_parents)

    def add_other_parent(self, offset, parent):
        self._other_parents.append((offset, parent))

    @property
    def fields(self):
        """Fields of the class without fields of parents by offset."""
        return dict(self._fields)

    @property
    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def add_method(self, method):
        self._methods.append(method)

    def add_other_method(self, method):
        self._other_methods.append(method)

    def find_other_method(self, method_name):
        """Find not virtual method, None if it's overloaded."""
        methods = [
            method for method in self._other_methods
            if method.proc_name == method_name
        ]
        return methods[0] if len(methods) == 1 else None

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
