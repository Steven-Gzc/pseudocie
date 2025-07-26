"""Environment abstraction used by the pseudocode interpreter.

Keeping this layer separate makes it easier to plug-in features such as:
    * type checking / coercion
    * persistent program state (e.g., save / restore)
    * dependency injection for I/O in unit tests

For now it is a very thin wrapper around two dictionaries.
"""
from __future__ import annotations

from typing import Any, Dict


class RuntimeError(Exception):
    """Base-class for runtime-level errors."""


class VariableAlreadyDeclared(RuntimeError):
    """Raised when attempting to redeclare an identifier."""


class VariableNotDeclared(RuntimeError):
    """Raised when an identifier is used before being declared."""


class ConstantRedefinition(RuntimeError):
    """Raised when attempting to assign to a constant."""


class Environment:
    """Mutable mapping holding variables and constants for a program run."""

    def __init__(self) -> None:
        self._vars: Dict[str, Any] = {}
        self._consts: Dict[str, Any] = {}
        self._types: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Declaration helpers
    # ------------------------------------------------------------------

    def declare_var(self, name: str, type_str: str) -> None:
        """Declare a variable *name* of *type_str* (e.g. ``INTEGER``)."""
        key = name.upper()
        if key in self:
            raise VariableAlreadyDeclared(f"Identifier '{name}' already declared.")
        self._vars[key] = None
        self._types[key] = type_str.upper()

    def define_const(self, name: str, value: Any) -> None:
        """Create a constant *name* bound to *value*."""
        key = name.upper()
        if key in self:
            raise VariableAlreadyDeclared(f"Identifier '{name}' already declared.")
        self._consts[key] = value

    # ------------------------------------------------------------------
    # Get / set
    # ------------------------------------------------------------------

    def set_var(self, name: str, value: Any) -> None:
        key = name.upper()
        if key in self._consts:
            raise ConstantRedefinition(f"Cannot re-assign to constant '{name}'.")
        if key not in self._vars:
            raise VariableNotDeclared(f"Variable '{name}' has not been declared.")
        self._vars[key] = value

    def get(self, name: str) -> Any:
        key = name.upper()
        if key in self._consts:
            return self._consts[key]
        if key in self._vars:
            return self._vars[key]
        raise VariableNotDeclared(f"Identifier '{name}' has not been declared.")

    # ------------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------------

    def __contains__(self, name: str) -> bool:  # type: ignore[override]
        key = name.upper()
        return key in self._vars or key in self._consts

    # Helpful for debugging / REPL visualisation
    def __repr__(self) -> str:  # noqa: D401 – prefer concise repr
        parts = [
            "Variables:" if self._vars else "No variables.",
            *(f"  {k} = {v!r}" for k, v in self._vars.items()),
            "Constants:" if self._consts else "No constants.",
            *(f"  {k} = {v!r}" for k, v in self._consts.items()),
        ]
        return "\n".join(parts) 