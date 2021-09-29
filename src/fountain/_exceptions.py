from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._ast import Token


class TokenizeError(RuntimeError):
    def __init__(self, lineno: int, message: str) -> None:
        super().__init__(message)
        self.lineno = lineno
        self.message = message


class ParseError(RuntimeError):
    def __init__(self, token: "Token", message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message

    @property
    def at_eof(self) -> bool:
        from ._ast import TokenType

        return self.token.type == TokenType.EOF


class EvalError(RuntimeError):
    def __init__(self, token: "Token", message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message
