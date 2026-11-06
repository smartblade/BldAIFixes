import data_types


class NewExpression:
    """Creation of an object by 'new T(arguments)'."""

    def __init__(self, class_type, arguments):
        self._class_type = class_type
        self._arguments = list(arguments)

    def __repr__(self):
        return "New({}, {})".format(
            self._class_type.class_name, self._arguments)

    @property
    def class_type(self):
        return self._class_type

    @property
    def arguments(self):
        return self._arguments

    @property
    def data_type(self):
        return data_types.Pointer32(self._class_type)

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        for argument in self._arguments:
            argument.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        arguments = [
            argument.transform(transformer, **kwargs)
            for argument in self._arguments
        ]
        if all(a is b for a, b in zip(arguments, self._arguments)):
            return self
        return self.__class__(self._class_type, arguments)

    def emit_code(self):
        return "new {}({})".format(
            self._class_type.class_name,
            ", ".join(argument.emit_code() for argument in self._arguments))
