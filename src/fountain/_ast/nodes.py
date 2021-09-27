from dataclasses import dataclass
from typing import Any

from .._tokens import Token


@dataclass
class Expr:
    pass


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Unary(Expr):
    op: Token
    right: Expr


@dataclass
class Binary(Expr):
    left: Expr
    op: Token
    right: Expr


@dataclass
class Group(Expr):
    expression: Expr
