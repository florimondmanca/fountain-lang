from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._ast import Token


class TokenizeError(RuntimeError):
    def __init__(self, lineno: int, message: str) -> None:
        super().__init__(message)
        self.lineno = lineno
        self.message = message


class TokenizeErrors(RuntimeError):
    def __init__(self, errors: list[TokenizeError]) -> None:
        super().__init__()
        self.errors = errors


class ParseError(RuntimeError):
    def __init__(self, token: "Token", message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message

    @property
    def at_eof(self) -> bool:
        from ._ast import TokenType

        return self.token.type == TokenType.EOF


class ParseErrors(RuntimeError):
    def __init__(self, errors: list[ParseError]) -> None:
        super().__init__()
        self.errors = errors


class EvalError(RuntimeError):
    def __init__(self, token: "Token", message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class Broke(Exception):
    pass


class Continued(Exception):
    pass


class Returned(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value
