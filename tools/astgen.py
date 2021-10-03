"""
Generate AST classes using metaprogramming.
"""

import argparse
import pathlib


def make_ast(groups: list[tuple[str, list[str]]]) -> str:
    lines = [
        "from dataclasses import dataclass",
        "from typing import Any, Optional",
        "",
        "from .tokens import Token",
        "",
    ]

    for basename, types in groups:
        lines += [
            "",
            "@dataclass(frozen=True)",
            f"class {basename}:",
            "    pass",
            "",
        ]

        for t in types:
            name, sep, fieldspec = t.partition("=")
            assert sep
            name = name.strip()
            fields = [f.strip() for f in fieldspec.strip().split(",") if f] or ["pass"]
            lines += [
                "",
                "@dataclass(frozen=True)",
                f"class {name}({basename}):",
                *(f"    {field}" for field in fields),
                "",
            ]

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    path = pathlib.Path(args.path)

    # Syntax: class_name = attr1: type1[, ...]
    expr_types = [
        "Disjunction   = expressions: list[Expr]",
        "Conjunction   = expressions: list[Expr]",
        "Binary        = left: Expr, op: Token, right: Expr",
        "Unary         = op: Token, right: Expr",
        "Call          = "
        + (
            "callee: Expr, pos_args: list[Expr], "
            "kw_names: list[Token], kw_values: list[Expr], closing: Token"
        ),
        "Literal       = value: Any",
        "Group         = expression: Expr",
        "Variable      = name: Token",
    ]
    stmt_types = [
        "Block      = statements: list[Stmt]",
        "If         = test: Expr, body: list[Stmt], orelse: list[Stmt]",
        "For        = body: list[Stmt]",
        "Break      = op: Token",
        "Continue   = op: Token",
        "Function   = "
        + (
            "name: Token, parameters: list[Token], defaults: list[Expr], "
            "body: list[Stmt]"
        ),
        "Return     = op: Token, expr: Optional[Expr]",
        "Assert     = op: Token, test: Expr, message: Optional[Expr]",
        "Assign     = target: Token, value: Expr",
        "Expression = expression: Expr",
    ]

    ast = make_ast(
        [
            ("Expr", expr_types),
            ("Stmt", stmt_types),
        ]
    )

    path.write_text(ast)
