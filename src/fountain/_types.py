from typing import Any, Callable

from ._ast import Function, Stmt
from ._environment import Environment
from ._exceptions import Returned


class FunctionType:
    @property
    def parameters(self) -> list[str]:
        raise NotImplementedError  # pragma: no cover

    @property
    def defaults(self) -> list[Any]:
        raise NotImplementedError  # pragma: no cover

    def call(self, *arguments: Any) -> Any:
        raise NotImplementedError  # pragma: no cover

    def __repr__(self) -> str:
        raise NotImplementedError  # pragma: no cover


class UserFunction(FunctionType):
    def __init__(
        self,
        stmt: Function,
        defaults: list[Any],
        closure: Environment,
        execute: Callable[[list[Stmt], Environment], None],
    ) -> None:
        self._stmt = stmt
        self._defaults = defaults
        self._closure = closure
        self._execute = execute

    @property
    def name(self) -> str:
        return self._stmt.name.lexeme

    @property
    def parameters(self) -> list[str]:
        return [param.lexeme for param in self._stmt.parameters]

    @property
    def defaults(self) -> list[Any]:
        return self._defaults

    def call(self, *arguments: Any) -> Any:
        environment = Environment(self._closure)

        for i, param in enumerate(self._stmt.parameters):
            environment.assign(param.lexeme, arguments[i])

        try:
            self._execute(self._stmt.body, environment)
        except Returned as exc:
            return exc.value
        else:
            return None

    def __repr__(self) -> str:
        return f"<function {self.name} at {hex(id(self))}>"
