import argparse
import pathlib
import sys

from ._ast import parse, tokenize
from ._exceptions import EvalError, ParseError, TokenizeError
from ._interpreter import Interpreter


def main() -> None:
    cli = CLI()
    ret = cli.main(sys.argv[1:])
    sys.exit(ret)


class CLI:
    def __init__(self) -> None:
        self._interpreter = Interpreter()

    def main(self, argv: list[str]) -> int:
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-c", "--command")
        group.add_argument("-p", dest="path")
        group.add_argument("-", dest="stdin", action="store_true", default=True)
        args = parser.parse_args(argv)

        if args.command is not None:
            return self.run(args.command)
        elif args.path:
            return self._run_file(args.path)
        else:
            return self._run_prompt()

    def run(self, source: str) -> int:
        try:
            tokens = tokenize(source)
        except TokenizeError as exc:
            self._report(exc.message, lineno=exc.lineno)
            return 65

        try:
            statements = parse(tokens)
        except ParseError as exc:
            where = "at end" if exc.at_eof else f"at {exc.token.lexeme!r}"
            self._report(exc.message, lineno=exc.token.lineno, where=where)
            return 65

        try:
            self._interpreter.interpret(statements)
        except EvalError as exc:
            where = f"at {exc.token.lexeme!r}"
            self._report(exc.message, lineno=exc.token.lineno, where=where)
            return 70

        return 0

    def _run_file(self, path: str) -> int:
        try:
            source = pathlib.Path(path).read_text()
        except FileNotFoundError as exc:
            message = f"Cannot open file {path!r}: {exc}"
            print(message)
            return 1

        return self.run(source)

    def _run_prompt(self) -> int:
        while True:
            print("> ", end="", flush=True)

            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                print()  # Show `^C`.
                break

            if not line:
                break

            _ = self.run(line)

        return 0

    def _report(self, message: str, *, lineno: int, where: str = "") -> None:
        where = f": {where}" if where else ""
        print(f"[line {lineno}] error{where}: {message}", file=sys.stderr)
