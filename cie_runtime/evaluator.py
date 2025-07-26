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
        resolved_value = self.get_value(value)
        self.env.set_var(ident, resolved_value)

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
        """
        OR operator
        look up the values of items and return the result of the OR operation
        """
        a, b = self.get_value(items[0]), self.get_value(items[1])
        return a or b

    def and_op(self, items):
        a, b = self.get_value(items[0]), self.get_value(items[1])
        return a and b

    def not_op(self, items):
        value = self.get_value(items[0])
        return not value

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
        left_val, right_val = self.get_value(left), self.get_value(right)
        if op == ">":
            return left_val > right_val
        if op == "<":
            return left_val < right_val
        if op == ">=":
            return left_val >= right_val
        if op == "<=":
            return left_val <= right_val
        if op == "==":
            return left_val == right_val
        if op == "!=":
            return left_val != right_val
        raise ValueError(f"Unsupported comparison operator: {op}")

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def add(self, items):
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left + right

    def sub(self, items):
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left - right

    def mul(self, items):
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left * right

    def div(self, items):
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left / right

    def int_div(self, items):  # noqa: D401 – matching rule name
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left // right

    def mod(self, items):
        left, right = self.get_value(items[0]), self.get_value(items[1])
        return left % right

    def neg(self, items):
        value = self.get_value(items[0])
        return -value

    # ------------------------------------------------------------------
    # Factors / atoms
    # ------------------------------------------------------------------

    def atom(self, items):
        node = items[0]
        return self.get_value(node)

    # ------------------------------------------------------------------
    # Literals
    # ------------------------------------------------------------------

    def literal(self, items):  # noqa: D401 – rule name as in grammar
        """Collapse the 'literal' rule to its contained Python value."""
        return items[0]

    # ------------------------------------------------------------------
    # Root
    # ------------------------------------------------------------------

    def start(self, items):  # noqa: D401 – lark root
        # All side-effects already executed; returning env makes unit-tests easy
        return self.env

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_value(self, identifier_or_value: Any) -> Any:
        """Get the actual value from an identifier or return the value as-is.
        
        This function handles:
        - Boolean literals (TRUE/FALSE) -> Python bool
        - Variable identifiers -> their stored values
        - Other values -> returned unchanged
        """
        if isinstance(identifier_or_value, str):
            # Handle boolean literals
            if identifier_or_value.upper() == "TRUE":
                return True
            elif identifier_or_value.upper() == "FALSE":
                return False
            # Handle variable lookup
            elif identifier_or_value.upper() in self.env:
                return self.env.get(identifier_or_value)
        return identifier_or_value

    def _resolve(self, value: Any) -> Any:
        """Turn identifiers into their runtime value(used by OUTPUT)."""
        return self.get_value(value)


# ----------------------------------------------------------------------
# Public helper
# ----------------------------------------------------------------------

def run(tree: Tree, *, env: Environment | None = None) -> Environment:
    """Execute *tree* and return the populated :class:`Environment`."""
    evaluator = Evaluator(env)
    evaluator.transform(tree)
    return evaluator.env 