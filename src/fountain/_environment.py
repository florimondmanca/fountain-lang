from typing import Any, Optional

from ._ast import Token
from ._exceptions import EvalError


class Environment:
    def __init__(self, parent: "Environment" = None) -> None:
        self._parent = parent
        self._values: dict[str, Any] = {}

    @property
    def parent(self) -> Optional["Environment"]:
        return self._parent

    def assign(self, name: str, value: Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> Any:
        try:
            return self._values[name.lexeme]
        except KeyError:
            raise EvalError(name, f"name {name.lexeme!r} is not defined") from None

    def get_at(self, depth: int, name: Token) -> Any:
        ancestor = self
        for _ in range(depth):
            assert ancestor.parent is not None
            ancestor = ancestor.parent
        return ancestor.get(name)
