"""
Generate AST classes using metaprogramming.
"""

import argparse
import pathlib


def make_ast(groups: list[tuple[str, list[str]]]) -> str:
    lines = [
        "from dataclasses import dataclass",
        "from typing import Any",
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
        "Conditional   = test: Expr, body: Expr, orelse: Expr",
    ]
    stmt_types = [
        "Expression = expression: Expr",
        "Print      = expression: Expr",
    ]

    ast = make_ast(
        [
            ("Expr", expr_types),
            ("Stmt", stmt_types),
        ]
    )

    path.write_text(ast)
