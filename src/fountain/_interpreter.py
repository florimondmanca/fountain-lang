from contextlib import contextmanager
from typing import Any, Iterator, Type

from ._ast import (
    Assert,
    Assign,
    Binary,
    Block,
    Break,
    Call,
    Conjunction,
    Continue,
    Disjunction,
    Expr,
    Expression,
    For,
    Function,
    Group,
    If,
    Literal,
    NodeVisitor,
    Return,
    Stmt,
    Token,
    TokenType,
    Unary,
    Variable,
)
from ._environment import Environment
from ._exceptions import Broke, Continued, EvalError, Returned
from ._types import FunctionType, UserFunction

__all__ = ["Interpreter"]


class Interpreter(NodeVisitor[Any]):
    def __init__(self) -> None:
        from ._builtins import BUILTINS  # Avoid import cycle.

        environment = Environment()
        for name, value in BUILTINS:
            environment.assign(name, value)

        self._globals = environment
        self._environment = environment
        self._locals: dict[Expr, int] = {}  # {variable: env depth, ...}

    def interpret(self, statements: list[Stmt]) -> Any:
        value: Any = None
        try:
            for stmt in statements:
                value = self.execute(stmt)
        except EvalError:
            raise
        else:
            return value

    def on_resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    #
    # Statements.
    #

    def execute_Block(self, stmt: Block) -> None:
        environment = Environment(self._environment)
        self._execute_in_environment(stmt.statements, environment)

    def _execute_in_environment(
        self, statements: list[Stmt], environment: Environment
    ) -> None:
        previous = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous

    def execute_If(self, stmt: If) -> None:
        test = self.evaluate(stmt.test)
        if is_truthy(test):
            for s in stmt.body:
                self.execute(s)
        else:
            for s in stmt.orelse:
                self.execute(s)

    def execute_For(self, stmt: For) -> None:
        while True:
            try:
                for s in stmt.body:
                    try:
                        self.execute(s)
                    except Continued:
                        break
            except Broke:
                break

    def execute_Break(self, stmt: Break) -> None:
        raise Broke()

    def execute_Continue(self, stmt: Continue) -> None:
        raise Continued()

    def execute_Function(self, stmt: Function) -> Any:
        defaults = [self.evaluate(default) for default in stmt.defaults]
        func = UserFunction(
            stmt,
            defaults,
            closure=self._environment,
            execute=self._execute_in_environment,
        )
        self._environment.assign(func.name, func)

    def execute_Return(self, stmt: Return) -> None:
        value = self.evaluate(stmt.expr) if stmt.expr is not None else None
        raise Returned(value)

    def execute_Assert(self, stmt: Assert) -> None:
        test = self.evaluate(stmt.test)

        if is_truthy(test):
            return

        message = (
            stringify(self.evaluate(stmt.message))
            if stmt.message is not None
            else "<assertion failed>"
        )

        raise EvalError(stmt.op, message)

    def execute_Assign(self, stmt: Assign) -> None:
        name = stmt.target.lexeme
        value = self.evaluate(stmt.value)
        self._environment.assign(name, value)

    def execute_Expression(self, stmt: Expression) -> Any:
        return self.evaluate(stmt.expression)

    #
    # Expressions.
    #

    def evaluate_Disjunction(self, expr: Disjunction) -> Any:
        for exp in expr.expressions:
            value = self.evaluate(exp)
            if is_truthy(value):
                return value
        return value

    def evaluate_Conjunction(self, expr: Conjunction) -> Any:
        for exp in expr.expressions:
            value = self.evaluate(exp)
            if not is_truthy(value):
                return value
        return value

    def evaluate_Binary(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.PLUS:
            with check_operands(expr.op, (TypeError, ValueError), left, right):
                return left + right

        if expr.op.type == TokenType.MINUS:
            with check_operands(expr.op, (TypeError, ValueError), left, right):
                return left - right

        if expr.op.type == TokenType.STAR:
            with check_operands(expr.op, (TypeError, ValueError), left, right):
                return left * right

        if expr.op.type == TokenType.SLASH:
            with check_operands(expr.op, (TypeError, ValueError), left, right):
                try:
                    return left / right
                except ZeroDivisionError:
                    raise EvalError(expr.op, "division by zero")

        if expr.op.type == TokenType.GREATER:
            with check_operands(expr.op, (TypeError,), left, right):
                return left > right

        if expr.op.type == TokenType.GREATER_EQUAL:
            with check_operands(expr.op, (TypeError,), left, right):
                return left >= right

        if expr.op.type == TokenType.LESS:
            with check_operands(expr.op, (TypeError,), left, right):
                return left < right

        if expr.op.type == TokenType.LESS_EQUAL:
            with check_operands(expr.op, (TypeError,), left, right):
                return left <= right

        if expr.op.type == TokenType.EQUAL_EQUAL:
            return left == right

        assert expr.op.type == TokenType.BANG_EQUAL
        return left != right

    def evaluate_Unary(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.MINUS:
            with check_operands(expr.op, (TypeError,), right):
                return -right

        assert expr.op.type == TokenType.NOT
        return not is_truthy(right)

    def evaluate_Call(self, expr: Call) -> Any:
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, FunctionType):
            raise EvalError(expr.closing, "can only call functions")

        pos_args = [self.evaluate(arg) for arg in expr.pos_args]
        kw_args = {
            name.lexeme: self.evaluate(value)
            for name, value in zip(expr.kw_names, expr.kw_values)
        }

        arguments = bind_arguments(expr, callee, *pos_args, **kw_args)

        return callee.call(*arguments)

    def evaluate_Literal(self, expr: Literal) -> Any:
        return expr.value

    def evaluate_Group(self, expr: Group) -> Any:
        return self.evaluate(expr.expression)

    def evaluate_Variable(self, expr: Variable) -> Any:
        depth = self._locals.get(expr)
        if depth is not None:
            return self._environment.get_at(depth, expr.name)
        return self._globals.get(expr.name)


class Empty:
    pass


EMPTY = Empty()


def bind_arguments(
    expr: Call, callee: FunctionType, *args: Any, **kwargs: Any
) -> list[Any]:
    # Follow Python's algorithm:
    # https://docs.python.org/3/reference/expressions.html#calls

    token = expr.closing

    slots = [EMPTY for _ in callee.parameters]

    # Put the N positional arguments in the first N slots.
    for i, arg in enumerate(args):
        try:
            slots[i] = arg
        except IndexError:
            arity = len(callee.parameters)
            plural = "" if arity == 1 else "s"
            raise EvalError(
                token, f"expected {arity} argument{plural}, got {len(args)}"
            )

    # Fill in corresponding slots for keyword arguments.
    for name, kwarg in kwargs.items():
        try:
            i = callee.parameters.index(name)
        except ValueError:
            raise EvalError(token, f"got an unexpected keyword argument: {name!r}")

        if slots[i] is not EMPTY:
            raise EvalError(token, f"got multiple values for argument {name!r}")

        slots[i] = kwarg

    try:
        slots.index(EMPTY)
    except ValueError:
        pass  # All slots filled.
    else:
        # Fill remaining values with defaults, in reverse (there may be
        # missing positional arguments we don't want to provide defaults for).
        for j, default in enumerate(reversed(callee.defaults), start=1):
            if slots[-j] is EMPTY:
                slots[-j] = default

    # Check for any empty values, indicating some positional arguments were missing.
    try:
        slots.index(EMPTY)
    except ValueError:
        pass  # All slots filled.
    else:
        missing = [p for i, p in enumerate(callee.parameters) if slots[i] is EMPTY]
        missinglist = ", ".join(repr(m) for m in missing)
        plural = "" if len(missing) == 1 else "s"
        raise EvalError(
            token,
            f"missing {len(missing)} positional argument{plural}: {missinglist}",
        )

    assert len(callee.parameters) == len(slots)

    return slots


@contextmanager
def check_operands(
    op: Token, exc_classes: tuple[Type[Exception], ...], *operands: Any
) -> Iterator[None]:
    try:
        yield
    except exc_classes:
        typelist = ", ".join(repr(typeify(operand)) for operand in operands)
        message = f"unsupported operand type(s) for {op.lexeme!r}: {typelist}"
        raise EvalError(op, message)


def stringify(value: Any) -> str:
    if value is None:
        return "nil"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, float):
        text = str(value)
        if text.endswith(".0"):
            return text[:-2]
        return text

    return str(value)


def typeify(value: Any) -> str:
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (float, int)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, FunctionType):
        return "function"
    raise NotImplementedError(f"Unknown type: {type(value)}")


def is_truthy(value: Any) -> bool:
    if value is None:
        return False

    if value == 0:
        return False

    if isinstance(value, bool):
        return value

    return True
