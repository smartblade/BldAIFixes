class SubscriptOperator:
    """Call of operator[] of an object: 'array[index]'."""

    def __init__(self, obj, index, data_type):
        self._obj = obj
        self._index = index
        self._data_type = data_type

    def __repr__(self):
        return "Subscript({}, {})".format(self._obj, self._index)

    @property
    def obj(self):
        return self._obj

    @property
    def index(self):
        return self._index

    @property
    def data_type(self):
        return self._data_type

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        self._obj.visit(on_expression_visited, **kwargs)
        self._index.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        obj = self._obj.transform(transformer, **kwargs)
        index = self._index.transform(transformer, **kwargs)
        if obj is self._obj and index is self._index:
            return self
        return self.__class__(obj, index, self._data_type)

    def emit_code(self):
        return "{}[{}]".format(self._obj.emit_code(), self._index.emit_code())
