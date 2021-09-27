import sys
import pathlib
from typing import Any, NamedTuple, Callable
from enum import Enum, auto


def cli() -> None:
    ft = Fountain()
    ft.main(sys.argv)


class Fountain:
    def __init__(self, on_exit: Callable[[int], None] = sys.exit) -> None:
        self._had_error = False
        self._on_exit = on_exit

    def main(self, argv: list[str]) -> None:
        if len(argv) > 2:
            print("Usage: fountain [script]")
            sys.exit(1)
        elif len(argv) == 2:
            self._run_file(argv[1])
        else:
            self._run_prompt()

    def _run_file(self, path: str) -> None:
        try:
            source = pathlib.Path(path).read_text()
        except FileNotFoundError as exc:
            print(f"Cannot open file {path!r}: {exc}")
            self._on_exit(1)
            return

        self._run(source)

        if self._had_error:
            self._on_exit(65)
            return

    def _run_prompt(self) -> None:
        while True:
            print("> ", end="", flush=True)

            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print()
            else:
                if not line:
                    break
                self._run(line)
                self.had_error = False

    def _run(self, source: str) -> None:
        def on_error(message: str, lineno: int) -> None:
            self._error(message, lineno=lineno)

        tokens = scan_tokens(source, on_error=on_error)

        for token in tokens:
            print(token)

    def _error(self, message: str, *, lineno: int) -> None:
        self._report(message, lineno=lineno)

    def _report(self, message: str, *, lineno: int, where: str = "") -> None:
        print(f"[line {lineno}] Error{where}: {message}", file=sys.stderr)
        self._had_error = True


class TokenType(Enum):
    # Single-character tokens
    LEFT_PARENS = auto()  # (
    RIGHT_PARENS = auto()  # `)`
    COMMA = auto()  # `,`
    DOT = auto()  # `.`
    PLUS = auto()  # `+`
    MINUS = auto()  # `-`
    STAR = auto()  # `*`
    SLASH = auto()  # `/`

    # One or two character tokens
    EQUAL = auto()  # `=`
    EQUAL_EQUAL = auto()  # `==`
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
    END = auto()  # `end`
    NIL = auto()  # `nil`
    FOR = auto()  # `for`
    IN = auto()  # `in`
    DO = auto()  # `do`
    FUN = auto()  # `fun`
    RETURN = auto()  # `return`
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
    "end": TokenType.END,
    "nil": TokenType.NIL,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "do": TokenType.DO,
    "fun": TokenType.FUN,
    "return": TokenType.RETURN,
}


def scan_tokens(
    source: str, on_error: Callable[[str, int], None] = lambda message, lineno: None
) -> list[Token]:
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
        if current + 1 > len(source):
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
                lineno += 1  # Allow multi-line strings.
            readnext()

        if done():
            on_error("unterminated string: EOF while scanning string literal", lineno)
            return

        # Add the closing quote.
        readnext()

        value = source[start + 1 : current - 1]  # Skip opening and closing quotes.
        add_token(TokenType.STRING, value=value)

    def readnumber() -> None:
        while (c := peek()).isdigit():
            readnext()

        if c == "." and peeknext().isdigit():  # Decimals.
            readnext()  # Skip the ".".
            while peek().isdigit():
                readnext()

        value = float(source[start:current])
        add_token(TokenType.NUMBER, value=value)

    def readidentifier() -> None:
        while peek().isalnum():
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
        elif c == "+":
            add_token(TokenType.PLUS)
        elif c == "*":
            add_token(TokenType.STAR)
        elif c == "/":
            add_token(TokenType.SLASH)
        # One or two character lexemes.
        elif c == "=":
            add_token(TokenType.EQUAL if matchnext("=") else TokenType.EQUAL_EQUAL)
        elif c == ">":
            add_token(TokenType.GREATER if matchnext("=") else TokenType.GREATER_EQUAL)
        elif c == "<":
            add_token(TokenType.LESS if matchnext("=") else TokenType.LESS_EQUAL)
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
        elif c.isdigit():
            readnumber()
        elif c.isalnum() or c == "_":
            readidentifier()
        else:
            on_error(f"invalid character: {c!r}", lineno)
            # Keep scanning.

    while not done():
        start = current
        scan_token()

    # Add final EOF.
    tokens.append(Token(type=TokenType.EOF, lineno=lineno))

    return tokens
