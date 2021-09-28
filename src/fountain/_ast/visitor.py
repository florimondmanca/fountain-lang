from typing import Generic, TypeVar

from .nodes import Expr, Stmt

R = TypeVar("R")


class NodeVisitor(Generic[R]):
    def evaluate(self, node: Expr) -> R:
        method = getattr(
            self, f"evaluate_{node.__class__.__name__}", self.evaluate_default
        )
        return method(node)

    def execute(self, node: Stmt) -> None:
        method = getattr(
            self, f"execute_{node.__class__.__name__}", self.execute_default
        )
        method(node)

    def evaluate_default(self, expr: Expr) -> R:
        raise NotImplementedError(f"Unexpected node: {expr}")  # pragma: no cover

    def execute_default(self, expr: Expr) -> None:
        raise NotImplementedError(f"Unexpected node: {expr}")  # pragma: no cover
