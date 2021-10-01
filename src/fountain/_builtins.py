import time
from typing import TYPE_CHECKING, Any

from ._functions import FunctionType

if TYPE_CHECKING:
    from ._interpreter import Interpreter


class Clock(FunctionType):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", *arguments: Any) -> Any:
        return time.time()

    def str(self) -> str:
        return "<built-in function clock>"


BUILTINS = [
    ("clock", Clock()),
]
