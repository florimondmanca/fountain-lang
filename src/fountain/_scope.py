from typing import Any

from ._ast import Token
from ._exceptions import EvalError


class Scope:
    def __init__(self, parent: "Scope" = None) -> None:
        self._parent = parent
        self._values: dict[str, Any] = {}

    def assign(self, name: str, value: Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> Any:
        try:
            return self._values[name.lexeme]
        except KeyError:
            if self._parent is not None:
                return self._parent.get(name)
            raise EvalError(name, f"name {name.lexeme!r} is not defined") from None
