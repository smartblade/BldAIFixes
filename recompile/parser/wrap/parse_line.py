from enum import Enum, auto

from expressions.operator import Operator, operators, priorities
import parser.wrap.tokens as tokens


class _StateKind(Enum):
    NONE = auto()
    LIST = auto()
    OP_LIST = auto()
    BRACKETS = auto()
    STRING = auto()


class _State:
    def __init__(self, kind: _StateKind):
        self._kind = kind
        self._list = []
        self._op_list = []
        self.operator_priority = None
        # Brackets of a call: 'f(...)', not of a condition or a group
        self.is_call = False
        # A comma separates arguments directly inside the brackets
        self.has_comma = False

    def __repr__(self):
        return "{}({})".format(self.__class__, self._kind)

    @property
    def list(self):
        assert self._kind == _StateKind.LIST
        return self._list

    @property
    def op_list(self):
        assert self._kind == _StateKind.OP_LIST
        return self._op_list

    @property
    def kind(self):
        return self._kind

    def validate_op_list(self):
        if len(self._op_list) == 0:
            return
        last_token, last_operator = self._op_list[-1]
        assert last_operator is not None


class _States:
    def __init__(self):
        self._states = [_State(_StateKind.NONE)]
        self._token = None
        self._buffer = []

    @property
    def cur_state(self):
        return self._states[-1]

    def new_state(self, kind):
        self._push_token()
        self.flush_buffer()
        new_state = _State(kind)
        self._states.append(new_state)
        return new_state

    def add_char(self, c):
        self._buffer.append(c)

    def mark_comma(self):
        """Mark the innermost brackets as containing several arguments."""
        for state in reversed(self._states):
            if state.kind == _StateKind.BRACKETS:
                state.has_comma = True
                return

    def is_after_name(self):
        """The buffer ends with a name, '(' after it opens a call."""
        return bool(self._buffer) and (
            self._buffer[-1].isalnum() or self._buffer[-1] == "_")

    def close_state(self, allow_brackets=False):
        if self.cur_state.kind == _StateKind.BRACKETS and not allow_brackets:
            raise Exception("Unexpected state {}.".format(self.cur_state.kind))
        state = self._states.pop()
        self._token = _make_token(state, self._token)

    def get_result(self):
        assert len(self._buffer) == 0
        assert len(self._states) == 1
        assert self.cur_state.kind == _StateKind.NONE
        assert self._token is not None
        return self._token

    def ensure_token(self):
        if self.cur_state.kind == _StateKind.LIST and self._token is None:
            self.close_state()
        assert self._token is not None

    def pop_token(self):
        assert self._token is not None
        token = self._token
        self._token = None
        return token

    def _push_token(self):
        if self._token is None:
            return
        cur_state = self.cur_state
        if cur_state.kind != _StateKind.LIST:
            cur_state = _State(_StateKind.LIST)
            self._states.append(cur_state)
        cur_state.list.append(self._token)
        self._token = None

    def pop_operator(self):
        return _pop_operator(self._buffer)

    def flush_buffer(self):
        if len(self._buffer) == 0:
            return
        any_code = tokens.AnyCodeToken("".join(self._buffer))
        self._buffer.clear()
        self._push_token()
        assert self._token is None
        self._token = any_code
        self._push_token()


def parse_line(line):
    states = _States()
    for c in line:
        if states.cur_state.kind == _StateKind.STRING:
            _add_string_char(states, c)
            continue
        if c == "(":
            is_call = states.is_after_name()
            states.new_state(_StateKind.BRACKETS).is_call = is_call
        elif c == ")":
            states.flush_buffer()
            _close_brackets(states)
        elif c == '"':
            states.new_state(_StateKind.STRING)
        else:
            states.add_char(c)
        operator = states.pop_operator()
        if operator is not None:
            if operator == Operator.COMMA:
                states.mark_comma()
            states.flush_buffer()
            _add_operator(states, operator)
    states.flush_buffer()
    while states.cur_state.kind != _StateKind.NONE:
        states.close_state()
    return states.get_result()


def _close_brackets(states):
    while states.cur_state.kind != _StateKind.BRACKETS:
        states.close_state()
    states.close_state(allow_brackets=True)


def _add_string_char(states, c):
    if c == '"':
        assert states.cur_state.kind == _StateKind.STRING
        states.flush_buffer()
        while states.cur_state.kind != _StateKind.STRING:
            states.close_state()
        states.close_state()
        return
    states.add_char(c)


def _make_token(state, token):
    if state.kind == _StateKind.LIST:
        return _make_list_token(state, token)
    if state.kind == _StateKind.OP_LIST:
        assert token is not None
        return _make_op_list_token(state, token)
    if state.kind == _StateKind.BRACKETS:
        return _make_brackets_token(state, token)
    if state.kind == _StateKind.STRING:
        return _make_string_token(state, token)
    raise Exception("Unexpected state {}.".format(state.kind))


def _make_list_token(state, token):
    assert state.kind == _StateKind.LIST
    tokens_list = list(state.list)
    if token is not None:
        tokens_list.append(token)
    return tokens.TokensList(tokens_list)


def _make_brackets_token(state, token):
    assert state.kind == _StateKind.BRACKETS
    if token is None:
        return tokens.AnyCodeToken("()")
    return tokens.BracketsToken(
        token, is_single_argument=state.is_call and not state.has_comma)


def _make_op_list_token(state, token):
    assert state.kind == _StateKind.OP_LIST
    state.validate_op_list()
    op_list = [*state.op_list, (token, None)]
    return tokens.OperatorSeparatedList(op_list)


def _make_string_token(state, token):
    assert isinstance(token, tokens.TokensList)
    assert len(token.tokens) == 1
    token = token.tokens[0]
    assert isinstance(token, tokens.AnyCodeToken)
    return tokens.StringToken(token.text)


def _pop_operator(buffer):
    if len(buffer) < 2:
        return None
    if buffer[-1] != ' ':
        return None
    if len(buffer) >= 3 and buffer[-3] == ' ':
        start = -3
    elif len(buffer) >= 4 and buffer[-4] == ' ':
        start = -4
    elif buffer[-2] == ',':
        start = -2
    else:
        return None
    op_pos = start
    if buffer[op_pos] == ' ':
        op_pos += 1
    operator = operators.get("".join(buffer[op_pos:-1]))
    if operator is None:
        return None
    for i in range(-start):
        buffer.pop()
    return operator


def _add_operator(states, operator):
    states.ensure_token()
    priority = priorities[operator]
    cur_state = states.cur_state
    if (
        cur_state.kind == _StateKind.OP_LIST and
        cur_state.operator_priority == priority
    ):
        cur_state.validate_op_list()
        cur_state.op_list.append((states.pop_token(), operator))
    elif (
        cur_state.kind == _StateKind.OP_LIST and
        cur_state.operator_priority < priority
    ):
        states.close_state()
        _add_operator(states, operator)
    else:
        token = states.pop_token()
        new_state = states.new_state(_StateKind.OP_LIST)
        new_state.operator_priority = priority
        new_state.validate_op_list()
        new_state.op_list.append((token, operator))
