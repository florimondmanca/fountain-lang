from enum import Enum, auto
from typing import Any, NamedTuple

from .._exceptions import TokenizeError, TokenizeErrors


class TokenType(Enum):
    # Single-character tokens
    LEFT_PARENS = auto()  # (
    RIGHT_PARENS = auto()  # `)`
    COMMA = auto()  # `,`
    DOT = auto()  # `.`
    SEMICOLON = auto()  # `;`
    PLUS = auto()  # `+`
    MINUS = auto()  # `-`
    STAR = auto()  # `*`
    SLASH = auto()  # `/`

    # One or two character tokens
    EQUAL = auto()  # `=`
    EQUAL_EQUAL = auto()  # `==`
    BANG_EQUAL = auto()  # `!=`
    GREATER = auto()  # `>`
    GREATER_EQUAL = auto()  # `>=`
    LESS = auto()  # `<`
    LESS_EQUAL = auto()  # `<=`

    # Literals
    IDENTIFIER = auto()  # var_name
    STRING = auto()  # `"str"`
    NUMBER = auto()  # `1`

    # Keywords
    TRUE = auto()  # `true`
    FALSE = auto()  # `false`
    AND = auto()  # `and`
    OR = auto()  # `or`
    NOT = auto()  # `not`
    IF = auto()  # `if`
    ELIF = auto()  # `elif`
    ELSE = auto()  # `else`
    DO = auto()  # `do`
    END = auto()  # `end`
    NIL = auto()  # `nil`
    FOR = auto()  # `for`
    BREAK = auto()  # `break`
    CONTINUE = auto()  # `continue`
    PASS = auto()  # `pass`
    IN = auto()  # `in`
    FN = auto()  # `fn`
    RETURN = auto()  # `return`
    ASSERT = auto()  # `assert`  # TODO: make it a function later
    EOF = auto()  # EOF


class Token(NamedTuple):
    type: TokenType
    lineno: int
    lexeme: str = ""
    value: Any = None


KEYWORDS = {
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "do": TokenType.DO,
    "end": TokenType.END,
    "nil": TokenType.NIL,
    "for": TokenType.FOR,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "pass": TokenType.PASS,
    "in": TokenType.IN,
    "fn": TokenType.FN,
    "assert": TokenType.ASSERT,
    "return": TokenType.RETURN,
}


def tokenize(source: str) -> list[Token]:
    tokens = []

    start = 0  # First character in the lexeme being scanned.
    current = 0  # Character currently being considered.
    lineno = 1  # What source line `current` is on.

    def done() -> bool:
        return current >= len(source)

    def add_token(type: TokenType, *, value: Any = None) -> None:
        # Add a token of a given type at the current position.
        lexeme = source[start:current]
        token = Token(type=type, lineno=lineno, lexeme=lexeme, value=value)
        tokens.append(token)

    def readnext() -> str:
        # Read and return the next character, advancing in
        # the source code scanning.
        nonlocal current
        c = source[current]
        current += 1
        return c

    def matchnext(expected: str) -> bool:
        # Return next character, if any.
        # This allows implementing one-character lookahead.
        nonlocal current
        if done():
            return False
        if source[current] != expected:
            return False
        current += 1
        return True

    def peek() -> str:
        # Return the current character, if any.
        if done():
            return "\0"
        return source[current]

    def peeknext() -> str:
        # Return the next character, if any.
        if current + 1 >= len(source):
            return "\0"
        return source[current + 1]

    def readstring(quote: str) -> None:
        nonlocal lineno

        # Read until next quote.
        while True:
            if done():
                break
            c = peek()
            if c == quote:
                break
            if c == "\n":
                message = "unterminated string: EOL while scanning string literal"
                raise TokenizeError(lineno, message)
            readnext()

        if done():
            message = "unterminated string: EOF while scanning string literal"
            raise TokenizeError(lineno, message)

        # Add the closing quote.
        readnext()

        value = source[start + 1 : current - 1]  # Skip opening and closing quotes.
        add_token(TokenType.STRING, value=value)

    def readnumber() -> None:
        while (c := peek()).isdigit():
            readnext()

        if c == ".":  # Decimals.
            readnext()  # Skip the ".".
            while peek().isdigit():
                readnext()

        value = float(source[start:current])
        add_token(TokenType.NUMBER, value=value)

    def readidentifier() -> None:
        while (c := peek()).isalnum() or c == "_":
            readnext()

        text = source[start:current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        add_token(token_type)

    def scan_token() -> None:
        nonlocal current, lineno

        c = readnext()

        # Single-character tokens, except `-` (as `--` is for comments).
        if c == "(":
            add_token(TokenType.LEFT_PARENS)
        elif c == ")":
            add_token(TokenType.RIGHT_PARENS)
        elif c == ",":
            add_token(TokenType.COMMA)
        elif c == ".":
            add_token(TokenType.DOT)
        elif c == ";":
            add_token(TokenType.SEMICOLON)
        elif c == "+":
            add_token(TokenType.PLUS)
        elif c == "*":
            add_token(TokenType.STAR)
        elif c == "/":
            add_token(TokenType.SLASH)
        # One or two character lexemes.
        elif c == "=":
            add_token(TokenType.EQUAL_EQUAL if matchnext("=") else TokenType.EQUAL)
        elif c == ">":
            add_token(TokenType.GREATER_EQUAL if matchnext("=") else TokenType.GREATER)
        elif c == "<":
            add_token(TokenType.LESS_EQUAL if matchnext("=") else TokenType.LESS)
        elif c == "!" and matchnext("="):
            add_token(TokenType.BANG_EQUAL)
        # Other lexemes.
        elif c == "-":
            if matchnext("-"):  # Comment, skip until end of line.
                while peek() != "\n" and not done():
                    readnext()
            else:
                add_token(TokenType.MINUS)
        elif c in (" ", "\r", "\t"):  # Whitespace.
            pass
        elif c == "\n":  # Newlines.
            lineno += 1
        elif c in ("'", '"'):
            readstring(quote=c)
        elif c.isdigit() and not peek().isalpha():
            readnumber()
        elif c.isalpha() or c == "_":
            readidentifier()
        else:
            raise TokenizeError(lineno, f"invalid character: {c!r}")

    errors = []

    while not done():
        start = current
        try:
            scan_token()
        except TokenizeError as exc:
            # We want to keep scanning to report as many errors as possible.
            # Gather errors in a list, then carry on.
            errors.append(exc)

    if errors:
        raise TokenizeErrors(errors)

    # Add final EOF.
    tokens.append(Token(type=TokenType.EOF, lineno=lineno))

    return tokens
