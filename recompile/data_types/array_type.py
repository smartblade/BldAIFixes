from data_types.data_type import DataType


class Array(DataType):
    def __init__(self, element_type, size):
        super().__init__()
        self._element_type = element_type
        self._size = size

    def __repr__(self):
        return "{}[{}]".format(self._element_type, self._size)

    @property
    def element_type(self):
        return self._element_type

    @property
    def length(self):
        return self._size

    @property
    def size(self):
        return self._size * self._element_type.size

    def make_variable_declaration(self, var_name):
        element_decl = self._element_type.make_variable_declaration(var_name)
        return "{}[{}]".format(element_decl, self._size)
