from typing import Generic, TypeVar

from .nodes import Binary, Expr, Group, Literal, Unary

R = TypeVar("R")


class NodeVisitor(Generic[R]):
    def visit(self, node: Expr) -> R:
        method = getattr(self, f"visit_{node.__class__.__name__}", self.default)
        return method(node)

    def default(self, expr: Expr) -> R:
        raise NotImplementedError(f"Unexpected node: {expr}")


class FountainPrinter(NodeVisitor[str]):
    """
    Shows an AST as Fountain would require it.
    """

    def visit_Literal(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_Unary(self, expr: Unary) -> str:
        return expr.op.lexeme + self.visit(expr.right)

    def visit_Binary(self, expr: Binary) -> str:
        return self.visit(expr.left) + f" {expr.op.lexeme} " + self.visit(expr.right)

    def visit_Group(self, expr: Group) -> str:
        return "(" + self.visit(expr.expression) + ")"


class DebugPrinter(NodeVisitor[str]):
    """
    Shows an AST in explicit Lisp-like style, for debugging.
    """

    def visit_Literal(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_Unary(self, expr: Unary) -> str:
        return f"({expr.op.lexeme} " + self.visit(expr.right) + ")"

    def visit_Binary(self, expr: Binary) -> str:
        return (
            f"({expr.op.lexeme} "
            + self.visit(expr.left)
            + " "
            + self.visit(expr.right)
            + ")"
        )

    def visit_Group(self, expr: Group) -> str:
        return "(group " + self.visit(expr.expression) + ")"


if __name__ == "__main__":
    import io

    from .._tokens import Token, TokenType
    from .nodes import Binary, Expr, Group, Literal, Unary

    # Consider the expression:
    # -3 * (12.4 + 2)
    expr = Binary(
        Unary(
            op=Token(TokenType.MINUS, 1, "-"),
            right=Literal(3),
        ),
        Token(TokenType.STAR, 1, "*"),
        Group(
            Binary(
                Literal(12.4),
                Token(TokenType.PLUS, 1, "+"),
                Literal(2),
            )
        ),
    )

    assert FountainPrinter().visit(expr) == "-3 * (12.4 + 2)"

    assert DebugPrinter().visit(expr) == "(* (- 3) (group (+ 12.4 2)))"

    # Extra: Reverse Polish Notation (RPN)

    class AstRPNPrinter(NodeVisitor[str]):
        def visit_Literal(self, expr: Literal) -> str:
            if expr.value is None:
                return "nil"
            return str(expr.value)

        def visit_Unary(self, expr: Unary) -> str:
            return self.visit(expr.right) + f" {expr.op.lexeme}"

        def visit_Binary(self, expr: Binary) -> str:
            return (
                self.visit(expr.left)
                + " "
                + self.visit(expr.right)
                + f" {expr.op.lexeme}"
            )

        def visit_Group(self, expr: Group) -> str:
            return self.visit(expr.expression)

    s = io.StringIO()
    assert AstRPNPrinter().visit(expr) == "3 - 12.4 2 + *"
