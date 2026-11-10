class MatrixDefinition:
    """Definition of all elements of a matrix by a macro, e.g.

    DEFINE_MATRIX(
        1.0, 0.0,
        0.0, 1.0
    )

    Each row is written on one line if all rows fit, otherwise each element
    of the matrix is on its own line.
    """

    def __init__(self, macro_name, rows):
        self._macro_name = macro_name
        self._rows = rows

    def __repr__(self):
        return "MatrixDefinition({}, {})".format(self._macro_name, self._rows)

    @property
    def macro_name(self):
        return self._macro_name

    @property
    def rows(self):
        return self._rows

    def visit(self, on_expression_visited, **kwargs):
        for row in self._rows:
            for element in row:
                element.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        rows = [
            [element.transform(transformer, **kwargs) for element in row]
            for row in self._rows
        ]
        return self.__class__(self._macro_name, rows)

    def emit_code(self, writer):
        writer.write_line("{}(".format(self._macro_name))
        rows = [
            [element.emit_code() for element in row] for row in self._rows]
        lines = [
            ", ".join(row) + ("" if index == len(rows) - 1 else ",")
            for index, row in enumerate(rows)
        ]
        with writer.indent():
            if not all(writer.fits(line) for line in lines):
                elements = [element for row in rows for element in row]
                lines = [
                    element + ("" if index == len(elements) - 1 else ",")
                    for index, element in enumerate(elements)
                ]
            for line in lines:
                writer.write_line(line)
        writer.write_line(")")
