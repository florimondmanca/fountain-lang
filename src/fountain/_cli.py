import argparse
import pathlib
import sys
from typing import Any

from ._ast import parse, resolve, tokenize
from ._exceptions import EvalError, ParseErrors, TokenizeErrors
from ._interpreter import Interpreter, stringify


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

    def evaluate(self, source: str) -> Any:
        try:
            tokens = tokenize(source)
        except TokenizeErrors as exc:
            for t_exc in exc.errors:
                self._report(t_exc.message, lineno=t_exc.lineno)
            raise

        try:
            statements = parse(tokens)
            resolve(self._interpreter, statements)
        except ParseErrors as exc:
            for p_exc in exc.errors:
                where = "at end" if p_exc.at_eof else f"at {p_exc.token.lexeme!r}"
                self._report(p_exc.message, lineno=p_exc.token.lineno, where=where)
            raise

        try:
            return self._interpreter.interpret(statements)
        except EvalError as exc:
            where = f"at {exc.token.lexeme!r}"
            self._report(exc.message, lineno=exc.token.lineno, where=where)
            raise

    def run(self, source: str) -> int:
        try:
            self.evaluate(source)
        except (TokenizeErrors, ParseErrors):
            return 65
        except EvalError:
            return 70
        else:
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
                continue

            if not line:
                break

            try:
                value = self.evaluate(line)
            except (TokenizeErrors, ParseErrors, EvalError):
                pass
            else:
                if value is not None:
                    print(stringify(value))

        return 0

    def _report(self, message: str, *, lineno: int, where: str = "") -> None:
        where = f": {where}" if where else ""
        print(f"[line {lineno}] error{where}: {message}", file=sys.stderr)
