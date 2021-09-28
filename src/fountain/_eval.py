import sys
from typing import Any, Callable, TextIO

from ._ast import (
    Binary,
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
)

__all__ = ["execute"]


def execute(
    statements: list[Stmt],
    on_error: Callable[[Token, str], None] = lambda token, message: None,
    stdout: TextIO = sys.stdout,
) -> None:
    interpreter = Interpreter(stdout=stdout)
    try:
        for stmt in statements:
            interpreter.execute(stmt)
    except EvalError as exc:
        on_error(exc.token, exc.message)
        return None


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


class Interpreter(NodeVisitor[Any]):
    def __init__(self, stdout: TextIO = sys.stdout) -> None:
        self._stdout = stdout

    def execute_Expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def execute_Print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value), file=self._stdout)

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
