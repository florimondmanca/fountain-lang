import time
from typing import Any

from ._functions import FunctionType
from ._interpreter import Interpreter, stringify


class Clock(FunctionType):
    parameters: list[str] = []
    defaults: list[str] = []

    def call(self, interpreter: Interpreter, *arguments: Any) -> Any:
        return time.time()

    def __str__(self) -> str:
        return "<built-in function clock>"


class Print(FunctionType):
    parameters = ["value"]
    defaults = [""]

    def call(self, interpreter: Interpreter, *arguments: Any) -> Any:
        (value,) = arguments
        print(stringify(value))

    def __str__(self) -> str:
        return "<built-in function print>"


BUILTINS = [
    ("clock", Clock()),
    ("print", Print()),
]
