from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from .._exceptions import ParseError, ParseErrors
from .nodes import (
    Assert,
    Assign,
    Binary,
    Block,
    Break,
    Call,
    Conjunction,
    Continue,
    Disjunction,
    Expression,
    For,
    Function,
    Group,
    If,
    Literal,
    Return,
    Stmt,
    Token,
    Unary,
    Variable,
)
from .visitor import NodeVisitor

if TYPE_CHECKING:
    from .._interpreter import Interpreter


def resolve(interpreter: "Interpreter", statements: list[Stmt]) -> None:
    resolver = Resolver(interpreter)
    errors = []

    for stmt in statements:
        try:
            resolver.execute(stmt)
        except ParseError as exc:
            errors.append(exc)

    if errors:
        raise ParseErrors(errors)


class Resolver(NodeVisitor[Any]):
    """
    Keep track of which scope a variable references belong to.

    This is implemented by traversing the syntax tree, taking note of
    the depth (global, scope 0, scope 1, ...) at which variable declaration
    (assignment, function definition) or usage occurs.

    This information is fed to the interpreter so that it evaluates variables
    from the appropriate scope (which may be different from the scope at the
    time of execution).
    """

    def __init__(self, interpreter: "Interpreter") -> None:
        self._interpreter = interpreter
        self._scopestack: list[dict[str, bool]] = []
        self._current_loop = ""
        self._current_function = ""

    @contextmanager
    def _scope(self) -> Iterator[None]:
        self._scopestack.append({})
        yield
        self._scopestack.pop()

    def _define(self, name: Token) -> None:
        if not self._scopestack:
            return
        current_scope = self._scopestack[-1]
        current_scope[name.lexeme] = True

    # Statements.

    def execute_Block(self, stmt: Block) -> None:
        with self._scope():
            for s in stmt.statements:
                self.execute(s)

    def execute_If(self, stmt: If) -> None:
        self.evaluate(stmt.test)
        for s in stmt.body:
            self.execute(s)
        for s in stmt.orelse:
            self.execute(s)

    def execute_For(self, stmt: For) -> None:
        enclosing_loop = self._current_loop
        self._current_loop = "for"

        for s in stmt.body:
            self.execute(s)

        self._current_loop = enclosing_loop

    def execute_Break(self, stmt: Break) -> None:
        if not self._current_loop:
            raise ParseError(stmt.op, "break outside loop")

    def execute_Continue(self, stmt: Continue) -> None:
        if not self._current_loop:
            raise ParseError(stmt.op, "continue outside loop")

    def execute_Function(self, stmt: Function) -> None:
        self._define(stmt.name)

        enclosing_function = self._current_function
        self._current_function = "function"

        with self._scope():
            for param in stmt.parameters:
                self._define(param)
            for s in stmt.body:
                self.execute(s)

        self._current_function = enclosing_function

    def execute_Return(self, stmt: Return) -> None:
        if not self._current_function:
            raise ParseError(stmt.op, "return outside function")

        if stmt.expr is not None:
            self.evaluate(stmt.expr)

    def execute_Assert(self, stmt: Assert) -> None:
        self.evaluate(stmt.test)
        if stmt.message is not None:
            self.evaluate(stmt.message)

    def execute_Assign(self, stmt: Assign) -> None:
        self._define(stmt.target)
        self.evaluate(stmt.value)

    def execute_Expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    # Expressions.

    def evaluate_Disjunction(self, expr: Disjunction) -> None:
        for exp in expr.expressions:
            self.evaluate(exp)

    def evaluate_Conjunction(self, expr: Conjunction) -> None:
        for exp in expr.expressions:
            self.evaluate(exp)

    def evaluate_Binary(self, expr: Binary) -> None:
        self.evaluate(expr.left)
        self.evaluate(expr.right)

    def evaluate_Unary(self, expr: Unary) -> None:
        self.evaluate(expr.right)

    def evaluate_Call(self, expr: Call) -> None:
        self.evaluate(expr.callee)
        for arg in expr.pos_args:
            self.evaluate(arg)
        for value in expr.kw_values:
            self.evaluate(value)

    def evaluate_Literal(self, expr: Literal) -> None:
        pass

    def evaluate_Group(self, expr: Group) -> None:
        self.evaluate(expr.expression)

    def evaluate_Variable(self, expr: Variable) -> None:
        # Let the interpreter know which depth the variable is located at.
        # Walk up from inner-most to outer-most scope.
        for depth, scope in enumerate(reversed(self._scopestack)):
            if expr.name.lexeme in scope:
                self._interpreter.on_resolve(expr, depth)
                break
