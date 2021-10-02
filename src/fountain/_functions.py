from typing import TYPE_CHECKING, Any

from ._ast import Function
from ._exceptions import ReturnExc
from ._scope import Scope

if TYPE_CHECKING:
    from ._interpreter import Interpreter


class FunctionType:
    def arity(self) -> int:
        raise NotImplementedError  # pragma: no cover

    def call(self, interpreter: "Interpreter", *arguments: Any) -> Any:
        raise NotImplementedError  # pragma: no cover

    def __str__(self) -> str:
        raise NotImplementedError  # pragma: no cover


class UserFunction(FunctionType):
    def __init__(self, stmt: Function, closure: Scope) -> None:
        self._stmt = stmt
        self._closure = closure

    @property
    def name(self) -> str:
        return self._stmt.name.lexeme

    def arity(self) -> int:
        return len(self._stmt.parameters)

    def call(self, interpreter: "Interpreter", *arguments: Any) -> Any:
        scope = Scope(self._closure)

        for i, param in enumerate(self._stmt.parameters):
            scope.assign(param.lexeme, arguments[i])

        try:
            interpreter.execute_scoped(self._stmt.body, scope)
        except ReturnExc as exc:
            return exc.value
        else:
            return None

    def __str__(self) -> str:
        return f"<function {self.name} at {hex(id(self))}>"