from parser.wrap.tokens.token import Token


class BracketsToken(Token):
    def __init__(self, token: Token, is_single_argument=False):
        super().__init__()
        assert token is not None
        self._token = token
        self._is_single_argument = is_single_argument

    @property
    def token(self):
        return self._token

    @property
    def is_single_argument(self):
        """Brackets of the only argument of a call: 'f(a + b)', not of
        several arguments, of a condition or of a group."""
        return self._is_single_argument

    def wrap(self, wrap_manager):
        wrap_manager.add_brackets(self)
