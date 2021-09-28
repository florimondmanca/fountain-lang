import sys
from typing import Any, Callable, TextIO

from ._ast import (
    Assert,
    Assign,
    Binary,
    Block,
    Conditional,
    Expression,
    Group,
    Literal,
    NodeVisitor,
    Print,
    Stmt,
    Token,
    TokenType,
    Unary,
    Variable,
)

__all__ = ["Interpreter"]


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


class EvalError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class Environment:
    def __init__(self, parent: "Environment" = None) -> None:
        self._parent = parent
        self._values: dict[str, Any] = {}

    def assign(self, name: str, value: Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> Any:
        try:
            return self._values[name.lexeme]
        except KeyError:
            if self._parent is not None:
                return self._parent.get(name)
            raise EvalError(name, f"name {name.lexeme!r} is not defined") from None


class Interpreter(NodeVisitor[Any]):
    def __init__(
        self,
        stdout: TextIO = sys.stdout,
        on_error: Callable[[Token, str], None] = lambda token, message: None,
    ) -> None:
        self._stdout = stdout
        self._on_error = on_error
        self._env = Environment()

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for stmt in statements:
                self.execute(stmt)
        except EvalError as exc:
            self._on_error(exc.token, exc.message)
            return None

    def execute_Assign(self, stmt: Assign) -> None:
        name = stmt.target.lexeme
        value = self.evaluate(stmt.value)
        self._env.assign(name, value)

    def execute_Expression(self, stmt: Expression) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value), file=self._stdout)

    def execute_Print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value), file=self._stdout)

    def execute_Assert(self, stmt: Assert) -> None:
        test = self.evaluate(stmt.test)

        if _is_truthy(test):
            return

        message = (
            stringify(self.evaluate(stmt.message))
            if stmt.message is not None
            else "<assertion failed>"
        )

        raise EvalError(stmt.op, message)

    def execute_Block(self, stmt: Block) -> None:
        previous = self._env
        env = Environment(parent=previous)
        try:
            self._env = env
            for statement in stmt.statements:
                self.execute(statement)
        finally:
            self._env = previous

    def evaluate_Literal(self, expr: Literal) -> Any:
        return expr.value

    def evaluate_Unary(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.MINUS:
            check_number_operand(expr.op, right)
            return -right

        assert expr.op.type == TokenType.NOT
        return not _is_truthy(right)

    def evaluate_Binary(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)

        # NOTE: evaluate operands lazily for logic operations.

        if expr.op.type == TokenType.AND:
            if _is_truthy(left):
                return self.evaluate(expr.right)
            return left

        if expr.op.type == TokenType.OR:
            if _is_truthy(left):
                return left
            return self.evaluate(expr.right)

        # All other operations require evaluating both operands.

        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.PLUS:
            check_add_operands(expr.op, left, right)
            return left + right

        if expr.op.type == TokenType.MINUS:
            check_number_operands(expr.op, left, right)
            return left - right

        if expr.op.type == TokenType.STAR:
            check_number_operands(expr.op, left, right)
            return left * right

        if expr.op.type == TokenType.SLASH:
            check_number_operands(expr.op, left, right)
            return left / right

        if expr.op.type == TokenType.GREATER:
            check_number_operands(expr.op, left, right)
            return left > right

        if expr.op.type == TokenType.GREATER_EQUAL:
            check_number_operands(expr.op, left, right)
            return left >= right

        if expr.op.type == TokenType.LESS:
            check_number_operands(expr.op, left, right)
            return left < right

        if expr.op.type == TokenType.LESS_EQUAL:
            check_number_operands(expr.op, left, right)
            return left <= right

        if expr.op.type == TokenType.EQUAL_EQUAL:
            return left == right

        assert expr.op.type == TokenType.BANG_EQUAL
        return left != right

    def evaluate_Group(self, expr: Group) -> Any:
        return self.evaluate(expr.expression)

    def evaluate_Conditional(self, expr: Conditional) -> Any:
        test = _is_truthy(self.evaluate(expr.test))
        if test:
            return self.evaluate(expr.body)
        return self.evaluate(expr.orelse)

    def evaluate_Variable(self, expr: Variable) -> Any:
        return self._env.get(expr.name)


def check_number_operand(op: Token, value: Any) -> None:
    if not isinstance(value, float):
        raise EvalError(op, "operand must be a number")


def check_add_operands(op: Token, left: Any, right: Any) -> None:
    if isinstance(left, float):
        check_number_operands(op, left, right)
        return

    if isinstance(left, str):
        if not isinstance(right, str):
            raise EvalError(op, "can only concatenate str to str")


def check_number_operands(op: Token, left: Any, right: Any) -> None:
    if not isinstance(left, float):
        raise EvalError(op, "left operand must be a number")

    if not isinstance(right, float):
        raise EvalError(op, "right operand must be a number")

    if op.type == TokenType.SLASH and right == 0:
        raise EvalError(op, "division by zero")


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False

    if value == 0:
        return False

    if isinstance(value, bool):
        return value

    return True
