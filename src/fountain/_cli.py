import pathlib
import sys
from typing import Callable

from ._tokens import scan_tokens


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
