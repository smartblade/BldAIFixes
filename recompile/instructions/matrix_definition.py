class MatrixDefinition:
    """Definition of all elements of a matrix by a macro, e.g.

    DEFINE_MATRIX(
        1.0, 0.0,
        0.0, 1.0
    )

    A row is written on one line if it fits, otherwise each element of the
    row is on its own line.
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
        with writer.indent():
            for row_index, row in enumerate(self._rows):
                is_last_row = row_index == len(self._rows) - 1
                elements = [element.emit_code() for element in row]
                line = ", ".join(elements) + ("" if is_last_row else ",")
                if writer.fits(line):
                    writer.write_line(line)
                    continue
                for element_index, element in enumerate(elements):
                    is_last = (
                        is_last_row and element_index == len(elements) - 1)
                    writer.write_line(element + ("" if is_last else ","))
        writer.write_line(")")
