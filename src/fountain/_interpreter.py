from typing import Any

from ._ast import (
    Assert,
    Assign,
    Binary,
    Block,
    Break,
    Conjunction,
    Continue,
    Disjunction,
    Expression,
    For,
    Group,
    If,
    Literal,
    NodeVisitor,
    Print,
    Stmt,
    Token,
    TokenType,
    Unary,
    Variable,
)
from ._exceptions import BreakExc, ContinueExc, EvalError

__all__ = ["Interpreter"]


class Interpreter(NodeVisitor[Any]):
    def __init__(self) -> None:
        self._scope = Scope()

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for stmt in statements:
                self.execute(stmt)
        except EvalError:
            raise

    def execute_Assign(self, stmt: Assign) -> None:
        name = stmt.target.lexeme
        value = self.evaluate(stmt.value)
        self._scope.assign(name, value)

    def execute_Expression(self, stmt: Expression) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def execute_Print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value))

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
                    except ContinueExc:
                        break
            except BreakExc:
                break

    def execute_Break(self, stmt: Break) -> None:
        raise BreakExc()

    def execute_Continue(self, stmt: Continue) -> None:
        raise ContinueExc()

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

    def execute_Block(self, stmt: Block) -> None:
        previous_scope = self._scope
        scope = Scope(parent=previous_scope)
        try:
            self._scope = scope
            for statement in stmt.statements:
                self.execute(statement)
        finally:
            self._scope = previous_scope

    def evaluate_Literal(self, expr: Literal) -> Any:
        return expr.value

    def evaluate_Unary(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.MINUS:
            check_number_operand(expr.op, right)
            return -right

        assert expr.op.type == TokenType.NOT
        return not is_truthy(right)

    def evaluate_Binary(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
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

    def evaluate_Variable(self, expr: Variable) -> Any:
        return self._scope.get(expr.name)


class Scope:
    def __init__(self, parent: "Scope" = None) -> None:
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


def is_truthy(value: Any) -> bool:
    if value is None:
        return False

    if value == 0:
        return False

    if isinstance(value, bool):
        return value

    return True
