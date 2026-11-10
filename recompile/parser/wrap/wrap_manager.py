from expressions.operator import Operator
import parser.wrap.tokens as tokens


class WrapManager:
    def __init__(self, max_line_len, indent_len, indent):
        self._wrap = max_line_len is not None
        self._indentation_required = True
        self._max_line_len = max_line_len
        self._indent_len = indent_len
        self._indent = indent
        self._current_pos = 0
        if indent_len is not None:
            self._lines_buffers = []
            self._new_line()
        else:
            self._lines_buffers = [[]]

    def get_lines(self):
        lines = []
        for buffer in self._lines_buffers:
            lines.append("".join(buffer))
        return lines

    def wrap_if_needed(self, token, indentation_required=None):
        if not self._wrap or self._can_add_to_current_line(token):
            self._add_to_current_line(token)
            return
        self._wrap_token(token, indentation_required)

    def _wrap_token(self, token, indentation_required=None):
        old_indentation_flag = self._indentation_required
        if indentation_required is not None:
            self._indentation_required = indentation_required
        token.wrap(self)
        indentation_done = (
            indentation_required if indentation_required is not None
            else old_indentation_flag
        ) and not self._indentation_required
        if indentation_done:
            self._do_unindent()
        self._indentation_required = old_indentation_flag

    def _can_add_to_current_line(self, token: tokens.Token = None, length=None):
        length = length or token.length
        offset = self._indent * self._indent_len + self._current_pos
        return offset + length <= self._max_line_len

    def _add_to_current_line(self, token: tokens.Token):
        old_wrap_flag = self._wrap
        self._wrap = False
        self._wrap_token(token)
        self._wrap = old_wrap_flag

    def _add_text_to_current_line(self, s: str):
        self._lines_buffers[-1].append(s)
        self._current_pos += len(s)

    def _add_operator(self, operator):
        text = operator.value
        if operator != Operator.COMMA:
            text = " " + text
        self._add_text_to_current_line(text)
        if self._wrap:
            self._new_line_and_ensure_indent()
        else:
            self._add_text_to_current_line(" ")

    def _add_opening_bracket(self):
        self._add_text_to_current_line("(")
        if self._wrap:
            self._new_line_and_indent()

    def _add_closing_bracket(self):
        if self._wrap:
            self._new_line_and_unindent()
        self._add_text_to_current_line(")")

    def _new_line(self):
        self._lines_buffers.append([" " * self._indent * self._indent_len])
        self._current_pos = 0

    def _do_indent(self):
        self._indent += 1

    def _do_unindent(self):
        self._indent -= 1

    def _new_line_and_indent(self):
        self._do_indent()
        self._new_line()

    def _new_line_and_ensure_indent(self):
        if self._indentation_required:
            self._do_indent()
            self._indentation_required = False
        self._new_line()

    def _new_line_and_unindent(self):
        self._do_unindent()
        self._new_line()

    def _flush_str_buffer(self, buffer, new_line=False):
        if len(buffer) == 0:
            return
        if new_line or self._can_add_to_current_line(length=len(buffer) + 1):
            self._add_text_to_current_line("".join(buffer))
            buffer.clear()
            return
        self._add_text_to_current_line('"')
        self._new_line_and_ensure_indent()
        self._add_text_to_current_line('"')
        self._flush_str_buffer(buffer, new_line=True)

    def add_tokens_list(self, tokens_list):
        for token in tokens_list.tokens:
            self._wrap_token(token)

    def add_any_code(self, any_code):
        self._add_text_to_current_line(any_code.text)

    def add_brackets(self, brackets):
        self._add_opening_bracket()
        # Continuation lines of the only argument of a call are indented
        # like those of each of several arguments, continuation lines of a
        # condition are not
        indentation_required = (
            brackets.is_single_argument and
            isinstance(brackets.token, tokens.OperatorSeparatedList))
        self._wrap_token(
            brackets.token, indentation_required=indentation_required)
        self._add_closing_bracket()

    def add_op_separated_list(self, op_list):
        for token, operator in op_list.pairs:
            self.wrap_if_needed(token, indentation_required=True)
            if operator is None:
                continue
            self._add_operator(operator)

    def add_string(self, s):
        self._add_text_to_current_line('"')
        if self._wrap:
            self._indentation_required = True
            buffer = []
            for c in s.string:
                buffer.append(c)
                if c == " ":
                    self._flush_str_buffer(buffer)
            self._flush_str_buffer(buffer)
            if not self._indentation_required:
                self._do_unindent()
        else:
            self._add_text_to_current_line(s.string)
        self._add_text_to_current_line('"')

