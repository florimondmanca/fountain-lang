"""
Generate AST classes using metaprogramming.
"""

import argparse
import pathlib


def make_ast(basename: str, types: list[str]) -> str:
    lines = []

    lines += [
        "from dataclasses import dataclass",
        "from typing import Any",
        "",
        "from .._tokens import Token",
        "",
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

    types = [
        # Syntax: class_name = attr1: type1[, ...]
        "Literal = value: Any",
        "Unary   = op: Token, right: Expr",
        "Binary  = left: Expr, op: Token, right: Expr",
        "Group   = expression: Expr",
    ]

    ast = make_ast("Expr", types)

    path.write_text(ast)
