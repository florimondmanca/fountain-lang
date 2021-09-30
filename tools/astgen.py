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
            "@dataclass",
            f"class {basename}:",
            "    pass",
            "",
        ]

        for t in types:
            name, sep, fieldspec = t.partition("=")
            assert sep
            name = name.strip()
            fields = [f.strip() for f in fieldspec.strip().split(",")]
            lines += [
                "",
                "@dataclass",
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
        "Literal       = value: Any",
        "Unary         = op: Token, right: Expr",
        "Binary        = left: Expr, op: Token, right: Expr",
        "Group         = expression: Expr",
        "Disjunction   = expressions: list[Expr]",
        "Conjunction   = expressions: list[Expr]",
        "Variable      = name: Token",
    ]
    stmt_types = [
        "Expression = expression: Expr",
        "Assign     = target: Token, value: Expr",
        "Print      = expression: Expr",
        "If         = test: Expr, body: list[Stmt], orelse: list[Stmt]",
        "Assert     = op: Token, test: Expr, message: Optional[Expr]",
        "Block      = statements: list[Stmt]",
    ]

    ast = make_ast(
        [
            ("Expr", expr_types),
            ("Stmt", stmt_types),
        ]
    )

    path.write_text(ast)
