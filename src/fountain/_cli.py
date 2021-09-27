import argparse
import pathlib
import sys
from typing import Callable

from ._ast import Token, TokenType, parse, tokenize, unparse_debug
from ._eval import evaluate, stringify


def cli() -> None:
    ft = Fountain()
    ft.main(sys.argv[1:])


class Fountain:
    def __init__(self, on_exit: Callable[[int], None] = sys.exit) -> None:
        self._had_error = False
        self._had_runtime_error = False
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
        if self._had_runtime_error:
            self._on_exit(70)

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
        if self._had_runtime_error:
            self._on_exit(70)

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
                self._had_error = False
                self._had_runtime_error = False

    def _run(self, source: str) -> None:
        tokens = tokenize(source, on_error=self._on_tokenize_error)
        # for token in tokens:
        #     print(token)
        expr = parse(tokens, on_error=self._on_parser_error)
        if expr is None:  # An error occurred.
            assert self._had_error
            return
        # print(unparse_debug(expr))
        print(stringify(evaluate(expr, on_error=self._on_eval_error)))

    def _on_tokenize_error(self, message: str, lineno: int) -> None:
        self._report(message, lineno=lineno)
        self._had_error = True

    def _on_parser_error(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            self._report(message, lineno=token.lineno, where=": at end")
        else:
            self._report(message, lineno=token.lineno, where=f": at {token.lexeme!r}")
        self._had_error = True

    def _on_eval_error(self, token: Token, message: str) -> None:
        self._report(message, lineno=token.lineno, where=f": at {token.lexeme!r}")
        self._had_runtime_error = True

    def _report(self, message: str, *, lineno: int, where: str = "") -> None:
        print(f"[line {lineno}] error{where}: {message}", file=sys.stderr)
