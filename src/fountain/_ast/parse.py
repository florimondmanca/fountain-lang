from .._exceptions import ParseError, ParseErrors
from .nodes import (
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
    Return,
    Stmt,
    Unary,
    Variable,
)
from .tokens import Token, TokenType


def parse(tokens: list[Token]) -> list[Stmt]:
    current = 0

    # Helpers.

    def peek() -> Token:
        return tokens[current]

    def previous() -> Token:
        return tokens[current - 1]

    def done() -> bool:
        return peek().type == TokenType.EOF

    def movenext() -> None:
        nonlocal current
        if not done():
            current += 1

    def check(t: TokenType) -> bool:
        if done():
            return False
        return peek().type == t

    def match(*types: TokenType) -> bool:
        for t in types:
            if check(t):
                movenext()
                return True
        return False

    def consume(t: TokenType, error_message: str) -> Token:
        if check(t):
            movenext()
            return previous()

        raise ParseError(peek(), error_message)

    # Syntax rules.

    def statement() -> Stmt:
        stmt = simple_statement()
        match(TokenType.SEMICOLON)  # In case of multi-statement line.
        return stmt

    def simple_statement() -> Stmt:
        if match(TokenType.DO):
            return block()

        if match(TokenType.IF):
            return if_statement()

        if match(TokenType.FOR):
            return for_statement()

        if match(TokenType.BREAK):
            return break_statement()

        if match(TokenType.CONTINUE):
            return continue_statement()

        if match(TokenType.FN):
            return function_statement()

        if match(TokenType.RETURN):
            return return_statement()

        if match(TokenType.ASSERT):
            return assert_statement()

        return assign_statement()

    def block() -> Stmt:
        statements = []
        while not check(TokenType.END) and not done():
            statements.append(statement())
        consume(TokenType.END, "expected 'end' after block")
        return Block(statements)

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

    def for_statement() -> Stmt:
        consume(TokenType.DO, "expected 'do' after 'for'")

        body = []
        while not check(TokenType.END) and not done():
            body.append(statement())

        consume(TokenType.END, "expected 'end' to close 'for'")

        return For(body)

    def break_statement() -> Stmt:
        return Break(previous())

    def continue_statement() -> Stmt:
        return Continue(previous())

    def function_statement() -> Stmt:
        name = consume(TokenType.IDENTIFIER, "expected function name")

        consume(TokenType.LEFT_PARENS, "expected '(' after function name")

        parameters = []  # N = n + m elements (n no-default, m with-default)
        defaults = []  # m elements
        expect_default = False
        num_no_default = 0

        if not check(TokenType.RIGHT_PARENS):
            while True:
                parameters.append(
                    consume(TokenType.IDENTIFIER, "expected parameter name")
                )

                if match(TokenType.EQUAL):
                    # Start parsing parameters with defaults.
                    expect_default = True
                    defaults.append(expression())
                elif expect_default:
                    raise ParseError(
                        previous(), "non-default parameter follows default parameter"
                    )
                else:
                    num_no_default += 1

                if not match(TokenType.COMMA):
                    break

        assert len(parameters) == num_no_default + len(defaults)

        consume(TokenType.RIGHT_PARENS, "expected ')' after parameters")

        body = []
        while not check(TokenType.END) and not done():
            body.append(statement())
        consume(TokenType.END, "expected 'end' to close function")

        return Function(name, parameters, defaults, body)

    def return_statement() -> Stmt:
        token = previous()
        expr = None if done() or match(TokenType.END) else expression()
        return Return(token, expr)

    def assert_statement() -> Stmt:
        op = previous()
        test = expression()
        message = expression() if match(TokenType.COMMA) else None
        return Assert(op, test, message)

    def assign_statement() -> Stmt:
        # May be `<expr>` or `<name> = <expr>` (assignment).
        # HACK: consume left-hand side as if it was an expression,
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
        return call()

    def call() -> Expr:
        expr = primary()

        # NOTE: there may be multiple calls, e.g. f(a, b)(c), where each
        # call becomes the callee of the next one.

        def finish_call(callee: Expr) -> Expr:
            pos_args: list[Expr] = []
            kw_names: list[Token] = []
            kw_values = []
            expect_kwarg = False

            if not check(TokenType.RIGHT_PARENS):
                while True:
                    if len(pos_args) + len(kw_names) >= 255:
                        raise ParseError(previous(), "more than 255 arguments")

                    value = expression()
                    valuetoken = previous()

                    if match(TokenType.EQUAL):
                        if not isinstance(value, Variable):
                            raise ParseError(
                                valuetoken, "argument name must be an identifier"
                            )
                        expect_kwarg = True
                        kw_names.append(value.name)
                        kw_values.append(expression())
                    elif expect_kwarg:
                        raise ParseError(
                            previous(), "non-default argument follows default argument"
                        )
                    else:
                        pos_args.append(value)

                    if not match(TokenType.COMMA):
                        break

            assert len(kw_names) == len(kw_values)

            closing = consume(TokenType.RIGHT_PARENS, "expected ')' after arguments")

            return Call(callee, pos_args, kw_names, kw_values, closing)

        while match(TokenType.LEFT_PARENS):
            expr = finish_call(callee=expr)

        return expr

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
                return

            # NOTE: we don't keep track of line ends, so we can only
            # guesstimate where the next statement starts.

            if previous().type == TokenType.END:
                return

            if peek().type in (
                TokenType.IDENTIFIER,  # x = ..., f()
                TokenType.DO,
                TokenType.IF,
                TokenType.FOR,
                TokenType.BREAK,
                TokenType.CONTINUE,
                TokenType.FN,
                TokenType.RETURN,
                TokenType.ASSERT,
                TokenType.SEMICOLON,  # <...> ;
            ):
                return

    statements = []
    errors = []

    while not done():
        try:
            statements.append(statement())
        except ParseError as exc:
            # We want to keep parsing to report as many errors as possible.
            # Gather errors in a list, synchronize parser state, then carry on.
            errors.append(exc)
            synchronize()

    if errors:
        raise ParseErrors(errors)

    return statements
