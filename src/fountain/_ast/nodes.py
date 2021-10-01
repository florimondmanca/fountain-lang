from dataclasses import dataclass
from typing import Any, Optional

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
class Disjunction(Expr):
    expressions: list[Expr]


@dataclass
class Conjunction(Expr):
    expressions: list[Expr]


@dataclass
class Variable(Expr):
    name: Token


@dataclass
class Call(Expr):
    callee: Expr
    arguments: list[Expr]
    closing: Token


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
class If(Stmt):
    test: Expr
    body: list[Stmt]
    orelse: list[Stmt]


@dataclass
class For(Stmt):
    body: list[Stmt]


@dataclass
class Break(Stmt):
    op: Token


@dataclass
class Continue(Stmt):
    op: Token


@dataclass
class Assert(Stmt):
    op: Token
    test: Expr
    message: Optional[Expr]


@dataclass
class Block(Stmt):
    statements: list[Stmt]


@dataclass
class Function(Stmt):
    name: Token
    parameters: list[Token]
    body: list[Stmt]


@dataclass
class Return(Stmt):
    op: Token
    expr: Optional[Expr]
