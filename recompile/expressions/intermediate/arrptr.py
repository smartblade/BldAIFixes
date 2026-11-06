import data_types


class Arrptr:
    def __init__(self, base, scale, index, offset):
        self._base = base
        self._scale = scale
        self._index = index
        self._offset = offset
        self._ptr32 = data_types.Pointer32()

    @property
    def base(self):
        return self._base

    @property
    def scale(self):
        return self._scale

    @property
    def index(self):
        return self._index

    @property
    def offset(self):
        return self._offset

    @property
    def data_type(self):
        return self._ptr32

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        self._base.visit(on_expression_visited, **kwargs)
        self._index.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        base = self._base.transform(transformer, **kwargs)
        index = self._index.transform(transformer, **kwargs)
        e = transformer.transform_arrptr(
            base, self._scale, index, self._offset, **kwargs)
        if e is not None:
            return e
        if base == self._base and index == self._index:
            return self
        return self.__class__(base, self._scale, index, self._offset)

    def emit_code(self):
        return "ARRPTR({}, {}, {}, {})".format(
            self._base.emit_code(),
            self._scale, self._index.emit_code(), self._offset)
