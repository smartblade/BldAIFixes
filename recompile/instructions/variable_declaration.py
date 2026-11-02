class VariableDeclaration:
    def __init__(
        self, identifier, initial_expression, is_direct_initialization=False
    ):
        self._id = identifier
        self._initial_expression = initial_expression
        # 'T x(a, b);' instead of 'T x = T(a, b);'
        self._is_direct_initialization = is_direct_initialization

    def __repr__(self):
        return "Decl({} {}={})".format(
            self._id.data_type, self._id.name, self._initial_expression
        )

    @property
    def initial_expression(self):
        return self._initial_expression

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        if self._initial_expression is not None:
            self._initial_expression.visit(on_expression_visited, **kwargs)

    def emit_code(self, writer):
        type_name = self._id.data_type.get_type_name()
        sep = "" if type_name.endswith("*") else " "
        initial_expression = ""
        if self._is_direct_initialization:
            initial_expression = "({})".format(", ".join(
                arg.emit_code() for arg in self._initial_expression.arguments))
        elif self._initial_expression is not None:
            initial_expression = " = " + self._initial_expression.emit_code()
        writer.write_line("{}{}{}{};".format(
                type_name, sep, self._id.name, initial_expression
            )
        )
