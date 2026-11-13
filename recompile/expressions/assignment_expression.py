class AssignmentExpression:
    """Assignment used as a value: 'b = a = x' is 'b = (a = x)'."""

    def __init__(self, dst, src):
        self._dst = dst
        self._src = src

    def __repr__(self):
        return "AssignExpr({}={})".format(self._dst, self._src)

    @property
    def data_type(self):
        return self._dst.data_type

    @property
    def dst(self):
        return self._dst

    @property
    def src(self):
        return self._src

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        self._src.visit(on_expression_visited, **kwargs)
        self._dst.visit(on_expression_visited, **kwargs)

    def transform(self, transform_callback, **kwargs):
        src = self._src.transform(transform_callback, **kwargs)
        dst = self._dst.transform(transform_callback, **kwargs)
        return transform_callback(AssignmentExpression(dst, src), **kwargs)

    def emit_code(self):
        return "{} = {}".format(self._dst.emit_code(), self._src.emit_code())
