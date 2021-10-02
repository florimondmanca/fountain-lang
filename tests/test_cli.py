import io
import sys
from typing import Any

import pytest

from fountain._cli import CLI


def test_cli_repl(monkeypatch: Any, capsys: Any) -> None:
    mock_stdin = io.StringIO("print 1 + 2")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    CLI().main([])
    captured = capsys.readouterr()
    assert captured.out == "> 3\n> "
    assert captured.err == ""


@pytest.mark.parametrize(
    "source, result",
    [
        ("print 1 + 2", "3\n"),
        ("print -2 * 3", "-6\n"),
        ("print 2 * (5-3.6)", "2.8\n"),
        ("print 3/4", "0.75\n"),
        ("print 'he' + 'llo'", "hello\n"),
        ("print true and true", "true\n"),
        ("print true and false", "false\n"),
        ("print true or false", "true\n"),
        ("print false or false", "false\n"),
        ("print nil or true", "true\n"),
        ("print 1 and 2", "2\n"),
        ("print 1 or 2", "1\n"),
        ("print 0 and 2", "0\n"),
        ("print 1 < 2", "true\n"),
        ("print 1 <= 2", "true\n"),
        ("print 2 <= 2", "true\n"),
        ("print 2 < 2", "false\n"),
        ("print 3 < 2", "false\n"),
        ("print 2 > 2", "false\n"),
        ("print 2 >= 2", "true\n"),
        ("print 3 >= 2", "true\n"),
        ("print 3 > 2", "true\n"),
        ("print 2 == 2", "true\n"),
        ("print 2 == 2.0", "true\n"),
        ("print 2 == 2.", "true\n"),
        ("print 2 != 2", "false\n"),
        ("print 2 != 2.1", "true\n"),
        ("print 2 != 'hello'", "true\n"),
        ("print true and 3 or 2", "3\n"),
        ("print false and 3 or 2", "2\n"),
        ("print 1 and 'yes' or 'no'", "yes\n"),
        ("print 1 and 2 or 4", "2\n"),
        ("print 0 and 2 or 4", "4\n"),
        ("print 1 or 2 and 4", "1\n"),
        ("print 0 or false and 4", "false\n"),
        ("print 0 or false or 1 and 4", "4\n"),
        ("print 1 + 2  -- Inline comment", "3\n"),
        ("x = 3; print x; print x + 2", "3\n5\n"),
        ("x = 3; print x; print x + 2", "3\n5\n"),
        (
            """
            x = 3
            print x
            print x + 2
            """,
            "3\n5\n",
        ),
        ("do end", ""),
        ("x = 0; do x = 1; print x; end; print x", "1\n0\n"),
        (
            """
            x = 0
            do
                x = 1
                print x
            end
            print x
            """,
            "1\n0\n",
        ),
        (
            """
            if 1 < 2 do
                print "yep"
            end
            """,
            "yep\n",
        ),
        (
            """
            if 1 > 2 do
                print "nah"
            else
                print "yep"
            end
            """,
            "yep\n",
        ),
        (
            """
            i = 0
            for do
                if i > 5 do
                    break
                end
                if i == 3 do
                    i = i + 1
                    continue
                end
                print i
                i = i + 1
            end
            """,
            "0\n1\n2\n4\n5\n",
        ),
        (
            "fn f() print 'OK' end; f()",
            "OK\n",
        ),
        (
            """
            fn add(x, y)
                return x + y
            end

            print add(1, 2)
            """,
            "3\n",
        ),
        (
            """
            fn adder(y)
                fn add(x)
                    return x + y
                end
                return add
            end

            add2 = adder(2)
            print add2(1)
            print adder(3)(2)
            """,
            "3\n5\n",
        ),
        ("assert true", ""),
        ("-- Comment", ""),
        ("", ""),
    ],
)
def test_cli_eval(source: str, result: str, capsys: Any) -> None:
    cli = CLI()
    cli.run(source)
    captured = capsys.readouterr()
    assert captured.out == result
    assert captured.err == ""


@pytest.mark.parametrize(
    "source, err, exit_code",
    [
        # Syntax errors
        (
            "(3 + 4",
            "[line 1] error: at end: expected ')' after expression\n",
            65,
        ),
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
        (
            "3 if true else 2",  # Ternary operator, not supported, use and/or instead.
            "[line 1] error: at 'else': expected 'do' after condition\n",
            65,
        ),
        (
            """
            if 1 < 2 do
                print 'yes'
            -- missing 'end'
            """,
            "[line 5] error: at end: expected 'end' to close 'if'\n",
            65,
        ),
        (
            """
            if 1 < 2 do
                print 'yes'
            else
                print 'no'
            -- missing 'end'
            """,
            "[line 7] error: at end: expected 'end' to close 'if'\n",
            65,
        ),
        (
            "3 = 12",
            "[line 1] error: at '=': cannot assign to literal\n",
            65,
        ),
        (
            "do x = 1",
            "[line 1] error: at end: expected 'end' after block\n",
            65,
        ),
        (
            "break",
            "[line 1] error: at 'break': break outside loop\n",
            65,
        ),
        (
            "continue",
            "[line 1] error: at 'continue': continue outside loop\n",
            65,
        ),
        (
            """
            for do
                print "missing end"
            """,
            "[line 4] error: at end: expected 'end' to close 'for'\n",
            65,
        ),
        (
            "fn f end",
            "[line 1] error: at 'end': expected '(' after function name\n",
            65,
        ),
        (
            "fn f( end",
            "[line 1] error: at 'end': expected parameter name\n",
            65,
        ),
        (
            "fn f(x end",
            "[line 1] error: at 'end': expected ')' after parameters\n",
            65,
        ),
        (
            "return 0",
            "[line 1] error: at 'return': return outside function\n",
            65,
        ),
        pytest.param(
            """
            x = "valid"
            !412
            y = "valid"
            §invalid
            """,
            (
                "[line 3] error: invalid character: '!'\n"
                "[line 5] error: invalid character: '§'\n"
            ),
            65,
            id="token-error-multiple",
        ),
        pytest.param(
            """
            fn valid() end
            valid())
            y = "valid"
            break
            z = "ok"
            """,
            (
                "[line 3] error: at ')': expected expression\n"
                "[line 5] error: at 'break': break outside loop\n"
            ),
            65,
            id="parse-error-multiple",
        ),
        # Runtime errors
        (
            "1/0",
            "[line 1] error: at '/': division by zero\n",
            70,
        ),
        (
            "1 + true",
            "[line 1] error: at '+': right operand must be a number\n",
            70,
        ),
        (
            "'hello' + 1",
            "[line 1] error: at '+': can only concatenate str to str\n",
            70,
        ),
        (
            "print x",
            "[line 1] error: at 'x': name 'x' is not defined\n",
            70,
        ),
        (
            "assert false",
            "[line 1] error: at 'assert': <assertion failed>\n",
            70,
        ),
        (
            "assert not true, 'false!'",
            "[line 1] error: at 'assert': false!\n",
            70,
        ),
        (
            "fn f(x, y) return x end; f(1)",
            "[line 1] error: at ')': expected 2 arguments, got 1\n",
            70,
        ),
        (
            "fn f(x) return x end; f(1, 2)",
            "[line 1] error: at ')': expected 1 argument, got 2\n",
            70,
        ),
        (
            "1()",
            "[line 1] error: at ')': can only call functions\n",
            70,
        ),
    ],
)
def test_cli_eval_error(source: str, err: str, exit_code: int, capsys: Any) -> None:
    assert CLI().run(source) == exit_code
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == err
