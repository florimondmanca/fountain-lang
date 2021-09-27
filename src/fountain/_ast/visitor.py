from typing import Generic, TypeVar

from .nodes import Expr

R = TypeVar("R")


class NodeVisitor(Generic[R]):
    def visit(self, node: Expr) -> R:
        method = getattr(self, f"visit_{node.__class__.__name__}", self.default)
        return method(node)

    def default(self, expr: Expr) -> R:
        raise NotImplementedError(f"Unexpected node: {expr}")
