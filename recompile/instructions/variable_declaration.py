class VariableDeclaration:
    def __init__(self, identifier, initial_expression):
        self._id = identifier
        self._initial_expression = initial_expression

    def __repr__(self):
        return "Decl({} {}={})".format(
            self._id.data_type, self._id.name, self._initial_expression
        )

    @property
    def identifier(self):
        return self._id

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
        if self._initial_expression is not None:
            initial_expression = " = " + self._initial_expression.emit_code()
        writer.write_line("{}{}{}{};".format(
                type_name, sep, self._id.name, initial_expression
            )
        )
