import io
import pytest

from fountain._cli import Fountain


def test_cli_repl() -> None:
    stdin = io.StringIO()
    stdin.write("1 + 2")
    stdin.seek(0)
    stdout = io.StringIO()
    stderr = io.StringIO()
    ft = Fountain(stdin=stdin, stdout=stdout, stderr=stderr)
    ft.main([])
    assert stdout.getvalue() == "> 3\n> "
    assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "source, result",
    [
        ("1 + 2", "3"),
        ("-2 * 3", "-6"),
        ("2 * (5-3.6)", "2.8"),
        ("3/4", "0.75"),
        ("'he' + 'llo'", "hello"),
        ("true and true", "true"),
        ("true and false", "false"),
        ("true or false", "true"),
        ("false or false", "false"),
        ("nil or true", "true"),
        ("1 and 2", "2"),
        ("1 or 2", "1"),
        ("0 and 2", "0"),
        ("1 < 2", "true"),
        ("1 <= 2", "true"),
        ("2 <= 2", "true"),
        ("2 < 2", "false"),
        ("3 < 2", "false"),
        ("2 > 2", "false"),
        ("2 >= 2", "true"),
        ("3 >= 2", "true"),
        ("3 > 2", "true"),
        ("2 == 2", "true"),
        ("2 == 2.0", "true"),
        ("2 == 2.", "true"),
        ("2 != 2", "false"),
        ("2 != 2.1", "true"),
        ("2 != 'hello'", "true"),
        ("1 + 2  -- Inline comment", "3"),
        ("-- Comment", "nil"),
        ("", "nil"),
    ],
)
def test_cli_eval(source: str, result: str) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    ft = Fountain(stdout=stdout, stderr=stderr)
    ft.main(["-c", source])
    assert stdout.getvalue() == f"{result}\n"
    assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "source, err, exit_code",
    [
        # Syntax errors
        ("(3 + 4", "[line 1] error: at end: expected ')' after expression\n", 65),
        (
            "'hello",
            "[line 1] error: unterminated string: EOF while scanning string literal\n",
            65,
        ),
        (
            "'hello\"",
            "[line 1] error: unterminated string: EOF while scanning string literal\n",
            65,
        ),
        (
            "'hello\n",
            "[line 1] error: unterminated string: EOL while scanning string literal\n",
            65,
        ),
        # Runtime errors
        ("1/0", "[line 1] error: at '/': division by zero\n", 70),
        ("1 + true", "[line 1] error: at '+': right operand must be a number\n", 70),
        (
            "'hello' + 1",
            "[line 1] error: at '+': can only concatenate str to str\n",
            70,
        ),
    ],
)
def test_cli_eval_error(source: str, err: str, exit_code: int) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_codes = []
    ft = Fountain(
        stdout=stdout, stderr=stderr, on_exit=lambda code: exit_codes.append(code)
    )
    ft.main(["-c", source])
    assert exit_codes == [exit_code]
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == err
