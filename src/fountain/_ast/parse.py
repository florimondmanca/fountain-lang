from .._exceptions import ParseError
from .nodes import (
    Assert,
    Assign,
    Binary,
    Block,
    Conjunction,
    Disjunction,
    Expr,
    Expression,
    Group,
    If,
    Literal,
    Print,
    Stmt,
    Unary,
    Variable,
)
from .tokens import Token, TokenType


def parse(tokens: list[Token]) -> list[Stmt]:
    current = 0

    # Helpers.

    def done() -> bool:
        return peek().type == TokenType.EOF

    def peek() -> Token:
        return tokens[current]

    def previous() -> Token:
        return tokens[current - 1]

    def movenext() -> None:
        nonlocal current
        if not done():
            current += 1

    def match(*types: TokenType) -> bool:
        for t in types:
            if check(t):
                movenext()
                return True
        return False

    def check(t: TokenType) -> bool:
        if done():
            return False
        return peek().type == t

    def consume(t: TokenType, error_message: str) -> None:
        if check(t):
            movenext()
            return

        raise ParseError(peek(), error_message)

    # Syntax rules.

    def statement() -> Stmt:
        stmt = simple_statement()
        match(TokenType.SEMICOLON)  # In case of multi-statement line.
        return stmt

    def simple_statement() -> Stmt:
        if match(TokenType.DO):
            return block()

        if match(TokenType.PRINT):
            return print_statement()

        if match(TokenType.IF):
            return if_statement()

        if match(TokenType.ASSERT):
            return assert_statement()

        # May be an expression (r-value), or an assignment (l-value = r-value).
        # Consume left-hand side as if it was an expression,
        # then make sure it is a valid variable if followed by '='.
        # This allows arbitrarily long assignment targets while
        # sticking to one-character lookahead.
        expr = expression()

        if match(TokenType.EQUAL):
            equals = previous()
            if isinstance(expr, Variable):
                target = expr.name
                value = expression()
                return Assign(target, value)
            dtype = expr.__class__.__name__.lower()
            raise ParseError(equals, f"cannot assign to {dtype}")

        return Expression(expr)

    def print_statement() -> Stmt:
        expr = expression()
        return Print(expr)

    def if_statement() -> Stmt:
        test = expression()
        consume(TokenType.DO, "expected 'do' after condition")

        body: list[Stmt] = []
        orelse: list[Stmt] = []
        target = body

        while True:
            if done():
                break
            if match(TokenType.ELSE):
                target = orelse
            if check(TokenType.END):
                break
            target.append(statement())

        consume(TokenType.END, "expected 'end' to close 'if'")

        return If(test, body, orelse)

    def assert_statement() -> Stmt:
        op = previous()
        test = expression()
        message = expression() if match(TokenType.COMMA) else None
        return Assert(op, test, message)

    def block() -> Stmt:
        statements = []
        while not check(TokenType.END) and not done():
            statements.append(statement())
        consume(TokenType.END, "expected 'end' after block")
        return Block(statements)

    def expression() -> Expr:
        return disjunction()

    def disjunction() -> Expr:
        expr = conjunction()
        if match(TokenType.OR):
            expressions = [expr, conjunction()]
            while match(TokenType.OR):
                expressions.append(conjunction())
            return Disjunction(expressions)
        return expr

    def conjunction() -> Expr:
        expr = equality()
        if match(TokenType.AND):
            expressions = [expr, equality()]
            while match(TokenType.AND):
                expressions.append(equality())
            return Conjunction(expressions)
        return expr

    def equality() -> Expr:
        expr = comparison()
        while match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = previous()
            right = comparison()
            expr = Binary(expr, op, right)
        return expr

    def comparison() -> Expr:
        expr = term()
        while match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            op = previous()
            right = term()
            expr = Binary(expr, op, right)
        return expr

    def term() -> Expr:
        expr = factor()
        while match(TokenType.PLUS, TokenType.MINUS):
            op = previous()
            right = term()
            expr = Binary(expr, op, right)
        return expr

    def factor() -> Expr:
        expr = unary()
        while match(TokenType.STAR, TokenType.SLASH):
            op = previous()
            right = unary()
            expr = Binary(expr, op, right)
        return expr

    def unary() -> Expr:
        if match(TokenType.MINUS, TokenType.NOT):
            op = previous()
            right = unary()
            return Unary(op, right)
        return primary()

    def primary() -> Expr:
        if match(TokenType.FALSE):
            return Literal(False)

        if match(TokenType.TRUE):
            return Literal(True)

        if match(TokenType.NIL) or not tokens:
            return Literal(None)

        if match(TokenType.NUMBER, TokenType.STRING):
            return Literal(previous().value)

        if match(TokenType.LEFT_PARENS):
            expr = expression()
            consume(TokenType.RIGHT_PARENS, "expected ')' after expression")
            return Group(expr)

        if match(TokenType.IDENTIFIER):
            return Variable(previous())

        raise ParseError(peek(), "expected expression")

    def synchronize() -> None:
        # Discard next tokens until we hit the beginning of the next statement.
        while True:
            movenext()

            if done():
                break

            if previous().type == TokenType.END:
                return

            if peek().type in (
                TokenType.FUN,
                TokenType.FOR,
                TokenType.IF,
                TokenType.RETURN,
            ):
                return

    statements = []
    try:
        while not done():
            statements.append(statement())
        return statements
    except ParseError:
        raise
