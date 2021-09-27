from .nodes import Binary, Expr, Group, Literal, Unary
from .visitor import NodeVisitor


class DebugRenderer(NodeVisitor[str]):
    """
    Render an AST in explicit Lisp-like style, for debugging.
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


def unparse_debug(expr: Expr) -> str:
    return DebugRenderer().visit(expr)


class LangRenderer(NodeVisitor[str]):
    """
    Render an AST in the style of our language.
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


def unparse(expr: Expr) -> str:
    return LangRenderer().visit(expr)


if __name__ == "__main__":
    import io

    from .tokens import Token, TokenType

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

    assert unparse_debug(expr) == "(* (- 3) (group (+ 12.4 2)))"

    assert unparse(expr) == "-3 * (12.4 + 2)"

    # Extra: Reverse Polish Notation (RPN)

    class RPNRenderer(NodeVisitor[str]):
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
    assert RPNRenderer().visit(expr) == "3 - 12.4 2 + *"
