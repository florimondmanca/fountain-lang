from .nodes import Expr


class NodeVisitor:
    def visit(self, node: Expr) -> None:
        method = getattr(self, f"visit_{node.__class__.__name__}", self.default)
        method(node)

    def default(self, expr: Expr) -> None:
        raise NotImplementedError(f"Unexpected node: {expr}")


if __name__ == "__main__":
    import io
    from typing import Callable

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

    # Let's pretty-print that expression tree into the above text form.

    class AstPrettyPrinter(NodeVisitor):
        def __init__(self, write: Callable) -> None:
            self.write = write

        def visit_Literal(self, expr: Literal) -> None:
            if expr.value is None:
                self.write("nil")
            self.write(str(expr.value))

        def visit_Unary(self, expr: Unary) -> None:
            self.write(expr.op.lexeme)
            self.visit(expr.right)

        def visit_Binary(self, expr: Binary) -> None:
            self.visit(expr.left)
            self.write(f" {expr.op.lexeme} ")
            self.visit(expr.right)

        def visit_Group(self, expr: Group) -> None:
            self.write("(")
            self.visit(expr.expression)
            self.write(")")

    s = io.StringIO()
    AstPrettyPrinter(write=s.write).visit(expr)
    assert s.getvalue() == "-3 * (12.4 + 2)"

    # And now, let's show it in a Lisp-like representation!

    class AstLispPrinter(NodeVisitor):
        def __init__(self, write: Callable) -> None:
            self.write = write

        def visit_Literal(self, expr: Literal) -> None:
            if expr.value is None:
                self.write("nil")
            self.write(str(expr.value))

        def visit_Unary(self, expr: Unary) -> None:
            self.write(f"({expr.op.lexeme} ")
            self.visit(expr.right)
            self.write(")")

        def visit_Binary(self, expr: Binary) -> None:
            self.write(f"({expr.op.lexeme} ")
            self.visit(expr.left)
            self.write(" ")
            self.visit(expr.right)
            self.write(")")

        def visit_Group(self, expr: Group) -> None:
            self.write("(group ")
            self.visit(expr.expression)
            self.write(")")

    s = io.StringIO()
    AstLispPrinter(write=s.write).visit(expr)
    assert s.getvalue() == "(* (- 3) (group (+ 12.4 2)))"

    # And finally, in Reverse Polish Notation (RPN)...

    class AstRPNPrinter(NodeVisitor):
        def __init__(self, write: Callable) -> None:
            self.write = write

        def visit_Literal(self, expr: Literal) -> None:
            if expr.value is None:
                self.write("nil")
            self.write(str(expr.value))

        def visit_Unary(self, expr: Unary) -> None:
            self.visit(expr.right)
            self.write(f" {expr.op.lexeme}")

        def visit_Binary(self, expr: Binary) -> None:
            self.visit(expr.left)
            self.write(" ")
            self.visit(expr.right)
            self.write(" ")
            self.write(expr.op.lexeme)

        def visit_Group(self, expr: Group) -> None:
            self.visit(expr.expression)

    s = io.StringIO()
    AstRPNPrinter(write=s.write).visit(expr)
    assert s.getvalue() == "3 - 12.4 2 + *"
