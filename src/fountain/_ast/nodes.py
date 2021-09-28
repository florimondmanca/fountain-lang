from dataclasses import dataclass
from typing import Any

from .tokens import Token


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


@dataclass
class Conditional(Expr):
    test: Expr
    body: Expr
    orelse: Expr


@dataclass
class Variable(Expr):
    name: Token


@dataclass
class Stmt:
    pass


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class Assign(Stmt):
    target: Token
    value: Expr


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Block(Stmt):
    statements: list[Stmt]
