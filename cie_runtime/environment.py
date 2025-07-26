class Environment:
    """A simple scoped environment for storing variables."""

    def __init__(self, parent: "Environment | None" = None):
        self._store: dict[str, object] = {}
        self.parent = parent

    # --- Declaration / lookup -------------------------------------------------

    def var_decl(self, name: str, value: object | None = None) -> None:
        if name in self._store:
            raise NameError(f"Variable '{name}' already declared in this scope")
        self._store[name] = value
    
    def const_decl(self, name: str, value: object | None = None) -> None:
        if name in self._store:
            raise NameError(f"Constant '{name}' already declared in this scope")
        self._store[name] = value

    def get(self, name: str) -> object:
        if name in self._store:
            return self._store[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' is not declared")

    def set(self, name: str, value: object) -> None:
        if name in self._store:
            self._store[name] = value
            return
        if self.parent is not None:
            self.parent.set(name, value)
            return
        raise NameError(f"Variable '{name}' is not declared")

    # --- Convenience ----------------------------------------------------------

    def __contains__(self, item: str) -> bool:  # pragma: no cover
        try:
            self.get(item)
            return True
        except NameError:
            return False

    def __repr__(self) -> str:  # pragma: no cover
        scopes = []
        env: Environment | None = self
        while env is not None:
            scopes.append(env._store)
            env = env.parent
        return " -> ".join(repr(s) for s in scopes) 