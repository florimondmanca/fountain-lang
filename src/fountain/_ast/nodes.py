from dataclasses import dataclass
from typing import Any, Optional

from .tokens import Token


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class Disjunction(Expr):
    expressions: list[Expr]


@dataclass(frozen=True)
class Conjunction(Expr):
    expressions: list[Expr]


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    op: Token
    right: Expr


@dataclass(frozen=True)
class Unary(Expr):
    op: Token
    right: Expr


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    pos_args: list[Expr]
    kw_names: list[Token]
    kw_values: list[Expr]
    closing: Token


@dataclass(frozen=True)
class Literal(Expr):
    value: Any


@dataclass(frozen=True)
class Group(Expr):
    expression: Expr


@dataclass(frozen=True)
class Variable(Expr):
    name: Token


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]


@dataclass(frozen=True)
class If(Stmt):
    test: Expr
    body: list[Stmt]
    orelse: list[Stmt]


@dataclass(frozen=True)
class For(Stmt):
    body: list[Stmt]


@dataclass(frozen=True)
class Break(Stmt):
    op: Token


@dataclass(frozen=True)
class Continue(Stmt):
    op: Token


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    parameters: list[Token]
    defaults: list[Expr]
    body: list[Stmt]


@dataclass(frozen=True)
class Return(Stmt):
    op: Token
    expr: Optional[Expr]


@dataclass(frozen=True)
class Assert(Stmt):
    op: Token
    test: Expr
    message: Optional[Expr]


@dataclass(frozen=True)
class Assign(Stmt):
    target: Token
    value: Expr


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr
