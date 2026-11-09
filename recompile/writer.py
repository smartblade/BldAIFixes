from contextlib import contextmanager

import parser


class Writer:
    def __init__(self, max_line_len=None, indent_length=4):
        self._lines = []
        self._max_line_len = max_line_len
        self._indent_length = indent_length
        self._indent = 0

    @property
    def indent_length(self):
        return self._indent_length

    def fits(self, line, indent=None):
        """Check if the line fits at the indent without wrapping."""
        indent = indent if indent is not None else self._indent
        return (
            self._max_line_len is None or
            indent * self._indent_length + len(line) <= self._max_line_len
        )

    def write_line(self, line="", indent=None):
        indent = indent if indent is not None else self._indent
        if line:
            self._add_line(line, indent)
        else:
            self._lines.append("")

    def _add_line(self, line, indent):
        if (
            self._max_line_len is None or
            indent * self._indent_length + len(line) <= self._max_line_len
        ):
            self._lines.append(" " * indent * self._indent_length + line)
            return
        lines = parser.wrap_line(
            line, self._max_line_len, self._indent_length, indent)
        self._lines.extend(lines)

    @contextmanager
    def indent(self):
        self._indent += 1
        try:
            yield self
        finally:
            self._unindent()

    def _unindent(self):
        self._indent -= 1

    def get_string(self):
        return "\n".join(self._lines) + "\n"
