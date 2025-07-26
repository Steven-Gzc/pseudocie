"""AST interpreter that walks the Lark parse tree and executes a
program written in CIE A-Level pseudocode.

This is **not** a full implementation – it only covers what the provided
`grammar.lark` currently understands:

* variable / constant declarations
* basic arithmetic & boolean expressions
* assignment
* simple INPUT / OUTPUT

Nonetheless, it gives students a *runnable* sandbox they can tinker with
while learning the language. The design purposefully keeps the public
surface small so that future language constructs (e.g. control-flow,
procedures, arrays) can slot in without breaking changes.
"""
from __future__ import annotations

from typing import Any, Callable

from lark import Token, Transformer, Tree

from .environment import Environment


class Evaluator(Transformer):
    """Transform-based interpreter.

    By subclassing ``lark.Transformer`` rather than ``Visitor`` we can
    evaluate expressions *bottom-up*: each rule returns a Python value
    that is immediately available to its parent rule.

    Parameters
    ----------
    env : Environment | None, default None
        Existing runtime mapping to mutate – useful for unit tests or
        REPLs. A fresh one is created when *None*.
    input_fn, output_fn : Callables, default built-ins
        Abstractions over ``input`` / ``print`` so tests can mock I/O.
    """

    def __init__(
        self,
        env: Environment | None = None,
        *,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[..., None] = print,
    ) -> None:
        super().__init__()
        self.env: Environment = env or Environment()
        self._input = input_fn
        self._output = output_fn

    # ------------------------------------------------------------------
    # Terminals – convert raw tokens into Python values
    # ------------------------------------------------------------------

    def IDENT(self, token: Token) -> str:  # noqa: N802 – lark convention
        return str(token)

    def INT_LITERAL(self, token: Token) -> int:  # noqa: N802
        return int(token)

    def REAL_LITERAL(self, token: Token) -> float:  # noqa: N802
        return float(token)

    def BOOL_LITERAL(self, token: Token) -> bool:  # noqa: N802
        return token.lower() == "true"

    def CHAR_LITERAL(self, token: Token) -> str:  # noqa: N802
        return token[1:-1]  # strip surrounding single quotes

    def STRING_LITERAL(self, token: Token) -> str:  # noqa: N802
        return bytes(token[1:-1], "utf-8").decode("unicode_escape")

    def DATE_LITERAL(self, token: Token) -> str:  # noqa: N802
        # TODO: convert into datetime.date when DATE semantics are firmed up
        return str(token)

    # ------------------------------------------------------------------
    # Declarations & Assignment
    # ------------------------------------------------------------------

    def var_decl(self, items):  # noqa: D401 – lark signature
        ident, type_tok = items
        self.env.declare_var(ident, str(type_tok))

    def const_decl(self, items):  # noqa: D401
        ident, value = items
        self.env.define_const(ident, value)

    def assign(self, items):  # noqa: D401
        ident, value = items
        self.env.set_var(ident, value)

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def input(self, items):
        ident: str = items[0]
        user_value = self._input(f"INPUT {ident}: ")
        # No automatic type coercion yet – stored as plain string
        self.env.set_var(ident, user_value)

    def output_list(self, items):
        return items  # simply propagate list of values upwards

    def output(self, items):
        # items[0] is the list produced by output_list
        resolved = [self._resolve(val) for val in items[0]]
        self._output(*resolved)

    # ------------------------------------------------------------------
    # Boolean logic
    # ------------------------------------------------------------------

    def or_op(self, items):
        a, b = items
        return a or b

    def and_op(self, items):
        a, b = items
        return a and b

    def not_op(self, items):
        return not items[0]

    # ------------------------------------------------------------------
    # Comparisons
    # ------------------------------------------------------------------

    def larger(self, _):
        return ">"

    def smaller(self, _):
        return "<"

    def largerequal(self, _):
        return ">="

    def smallerequal(self, _):
        return "<="

    def equal(self, _):
        return "=="

    def notequal(self, _):
        return "!="

    def compare(self, items):
        left, op, right = items
        if op == ">":
            return left > right
        if op == "<":
            return left < right
        if op == ">=":
            return left >= right
        if op == "<=":
            return left <= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        raise ValueError(f"Unsupported comparison operator: {op}")

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def add(self, items):
        return items[0] + items[1]

    def sub(self, items):
        return items[0] - items[1]

    def mul(self, items):
        return items[0] * items[1]

    def div(self, items):
        return items[0] / items[1]

    def int_div(self, items):  # noqa: D401 – matching rule name
        return items[0] // items[1]

    def mod(self, items):
        return items[0] % items[1]

    def neg(self, items):
        return -items[0]

    # ------------------------------------------------------------------
    # Factors / atoms
    # ------------------------------------------------------------------

    def atom(self, items):
        node = items[0]
        if isinstance(node, str) and node.upper() in self.env:
            return self.env.get(node)
        return node

    # ------------------------------------------------------------------
    # Root
    # ------------------------------------------------------------------

    def start(self, items):  # noqa: D401 – lark root
        # All side-effects already executed; returning env makes unit-tests easy
        return self.env

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve(self, value: Any) -> Any:
        """Turn identifiers into their runtime value (used by OUTPUT)."""
        if isinstance(value, str) and value.upper() in self.env:
            return self.env.get(value)
        return value


# ----------------------------------------------------------------------
# Public helper
# ----------------------------------------------------------------------

def run(tree: Tree, *, env: Environment | None = None) -> Environment:
    """Execute *tree* and return the populated :class:`Environment`."""
    evaluator = Evaluator(env)
    evaluator.transform(tree)
    return evaluator.env 