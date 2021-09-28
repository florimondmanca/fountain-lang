from typing import Callable, Optional

from .nodes import Binary, Expr, Group, Literal, Unary
from .tokens import Token, TokenType


class ParseError(RuntimeError):
    pass


def parse(
    tokens: list[Token],
    on_error: Callable[[Token, str], None] = lambda token, message: None,
) -> Optional[Expr]:
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

    def error(token: Token, message: str) -> Exception:
        on_error(token, message)
        return ParseError()

    def consume(t: TokenType, error_message: str) -> None:
        if check(t):
            movenext()
            return

        raise error(peek(), error_message)

    # Syntax rules.

    def expression() -> Expr:
        return equality()

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
            TokenType.AND,
            TokenType.OR,
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

        if match(TokenType.NIL) or done():
            return Literal(None)

        if match(TokenType.NUMBER, TokenType.STRING):
            return Literal(previous().value)

        if match(TokenType.LEFT_PARENS):
            expr = expression()
            consume(TokenType.RIGHT_PARENS, "expected ')' after expression")
            return Group(expr)

        raise error(peek(), "expected expression")

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

    try:
        return expression()
    except ParseError:
        return None
