from typing import Any

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
    Expression,
    For,
    Function,
    Group,
    If,
    Literal,
    NodeVisitor,
    Print,
    Return,
    Stmt,
    Token,
    TokenType,
    Unary,
    Variable,
)
from ._builtins import BUILTINS
from ._exceptions import BreakExc, ContinueExc, EvalError, ReturnExc
from ._functions import FunctionType, UserFunction
from ._scope import Scope

__all__ = ["Interpreter"]


class Interpreter(NodeVisitor[Any]):
    def __init__(self) -> None:
        scope = Scope()
        for name, value in BUILTINS:
            scope.assign(name, value)
        self._scope = scope

    def interpret(self, statements: list[Stmt]) -> Any:
        value: Any = None
        try:
            for stmt in statements:
                value = self.execute(stmt)
        except EvalError:
            raise
        else:
            return value

    def execute_Assign(self, stmt: Assign) -> None:
        name = stmt.target.lexeme
        value = self.evaluate(stmt.value)
        self._scope.assign(name, value)

    def execute_Expression(self, stmt: Expression) -> Any:
        return self.evaluate(stmt.expression)

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

    def execute_Return(self, stmt: Return) -> None:
        value = self.evaluate(stmt.expr) if stmt.expr is not None else None
        raise ReturnExc(value)

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
        scope = Scope(self._scope)
        self.execute_scoped(stmt.statements, scope)

    def execute_scoped(self, statements: list[Stmt], scope: Scope) -> None:
        previous_scope = self._scope
        try:
            self._scope = scope
            for statement in statements:
                self.execute(statement)
        finally:
            self._scope = previous_scope

    def execute_Function(self, stmt: Function) -> Any:
        func = UserFunction(stmt, closure=self._scope)
        self._scope.assign(func.name, func)

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

    def evaluate_Call(self, expr: Call) -> Any:
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, FunctionType):
            raise EvalError(expr.closing, "can only call functions")

        numargs, arity = len(expr.arguments), callee.arity()
        if numargs != arity:
            plural = "" if arity == 1 else "s"
            message = f"expected {arity} argument{plural}, got {numargs}"
            raise EvalError(expr.closing, message)

        arguments = [self.evaluate(arg) for arg in expr.arguments]

        return callee.call(self, *arguments)


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
