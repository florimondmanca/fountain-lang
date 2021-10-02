import time
from typing import Any

from ._functions import FunctionType
from ._interpreter import Interpreter, stringify


class Clock(FunctionType):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: Interpreter, *arguments: Any) -> Any:
        return time.time()

    def str(self) -> str:
        return "<built-in function clock>"


class Print(FunctionType):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: Interpreter, *arguments: Any) -> Any:
        (value,) = arguments
        print(stringify(value))

    def str(self) -> str:
        return "<built-in function print>"


BUILTINS = [
    ("clock", Clock()),
    ("print", Print()),
]
