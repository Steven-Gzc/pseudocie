from __future__ import annotations

import re
from typing import Any, Dict


class Environment:
    """Variable/constant storage with simple type checking."""

    _TYPE_MAP = {
        "INTEGER": int,
        "REAL": float,
        "STRING": str,
        "BOOLEAN": bool,
        "CHAR": str,
        "DATE": str,
        "const": object,
    }

    def __init__(self, parent: "Environment | None" = None):
        # Each entry: {"type": TYPE_NAME or 'const', "value": object}
        self._store: Dict[str, Dict[str, Any]] = {}
        self.parent = parent

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    def var_decl(self, name: str, type_name: str, value: Any | None = None) -> None:
        if name in self._store:
            raise NameError(f"Variable '{name}' already declared in this scope")
        self._assert_valid_type_name(type_name)
        if value is not None and not self._value_matches_type(value, type_name):
            raise TypeError(
                f"Initial value for '{name}' does not match declared type {type_name}"
            )
        self._store[name] = {"type": type_name, "value": value}

    def const_decl(self, name: str, value: Any) -> None:
        if name in self._store:
            raise NameError(f"Constant '{name}' already declared in this scope")
        # Constants are marked by special type 'const'.
        self._store[name] = {"type": "const", "value": value}

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get(self, name: str) -> Any:
        entry = self._lookup_entry(name)
        return entry["value"]

    def get_type(self, name: str) -> str:
        entry = self._lookup_entry(name)
        return entry["type"]

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set(self, name: str, value: Any) -> None:
        entry = self._lookup_entry(name)
        entry_type = entry["type"]
        if entry_type == "const":
            raise TypeError(f"Cannot assign to constant '{name}'")
        expected_type = entry_type
        if not self._value_matches_type(value, expected_type):
            raise TypeError(
                f"Type mismatch for '{name}': expected {expected_type}, got {type(value).__name__}"
            )
        entry["value"] = value

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lookup_entry(self, name: str) -> Dict[str, Any]:
        if name in self._store:
            return self._store[name]
        if self.parent is not None:
            return self.parent._lookup_entry(name)  # noqa: SLF001
        raise NameError(f"Variable '{name}' is not declared")

    @classmethod
    def _assert_valid_type_name(cls, type_name: str) -> None:
        if type_name not in cls._TYPE_MAP:
            raise ValueError(f"Unsupported type '{type_name}'")

    @classmethod
    def _value_matches_type(cls, value: Any, type_name: str) -> bool:
        if type_name == "const":
            return True
        py_type = cls._TYPE_MAP.get(type_name)
        if py_type is None:
            return True  # unknown types considered compatible
        if type_name == "CHAR":
            return isinstance(value, str) and len(value) == 1
        if type_name == "REAL":
            return isinstance(value, (int, float))
        return isinstance(value, py_type)

    @classmethod
    def _infer_type_name(cls, value: Any) -> str:
        if isinstance(value, bool):
            return "BOOLEAN"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        if isinstance(value, str):
            return "STRING"
        return "STRING"

    def __contains__(self, item: str) -> bool:  # pragma: no cover
        try:
            self._lookup_entry(item)
            return True
        except NameError:
            return False

    def __repr__(self) -> str:  # pragma: no cover
        scopes = []
        env: Environment | None = self
        while env is not None:
            scopes.append({k: v["value"] for k, v in env._store.items()})
            env = env.parent
        return " -> ".join(repr(s) for s in scopes) 