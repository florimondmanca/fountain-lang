import argparse
import pathlib
import sys
from typing import Callable

from ._ast.parse import parse
from ._ast.visitor import DebugPrinter
from ._tokens import Token, TokenType, scan_tokens


def cli() -> None:
    ft = Fountain()
    ft.main(sys.argv[1:])


class Fountain:
    def __init__(self, on_exit: Callable[[int], None] = sys.exit) -> None:
        self._had_error = False
        self._on_exit = on_exit

    def main(self, argv: list[str]) -> None:
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-c", "--command")
        group.add_argument("-p", dest="path")
        group.add_argument("-", dest="stdin", action="store_true", default=True)
        args = parser.parse_args(argv)

        if args.command:
            self._run_command(args.command)
        elif args.path:
            self._run_file(args.path)
        else:
            self._run_prompt()

    def _run_command(self, command: str) -> None:
        self._run(command)

        if self._had_error:
            self._on_exit(65)

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
        tokens = scan_tokens(source, on_error=self._on_scan_error)

        for token in tokens:
            print(token)

        if self._had_error:
            return

        expr = parse(tokens, on_error=self._on_parser_error)

        if self._had_error:
            return

        assert expr is not None

        print(DebugPrinter().visit(expr))

    def _on_scan_error(self, message: str, lineno: int) -> None:
        self._report(message, lineno=lineno)

    def _on_parser_error(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            self._report(message, lineno=token.lineno, where=": at end")
        else:
            self._report(message, lineno=token.lineno, where=f": at {token.lexeme!r}")

    def _report(self, message: str, *, lineno: int, where: str = "") -> None:
        print(f"[line {lineno}] error{where}: {message}", file=sys.stderr)
        self._had_error = True
