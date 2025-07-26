from __future__ import annotations

from lark import Token, Tree, Visitor

from .environment import Environment


class Evaluator(Visitor):
    """Walks the parse tree produced by *grammar.lark* and executes it."""

    def __init__(self, env: Environment | None = None):
        super().__init__()
        self.env = env or Environment()

    # ---------------------------------------------------------------------
    # Statement handlers (rules are named via '->' in grammar)
    # ---------------------------------------------------------------------

    def var_decl(self, tree: Tree):
        # Expect pattern: IDENT, TYPE (':' token is dropped by grammar)
        ident_token: Token = tree.children[0]
        type_token: Token = tree.children[1]
        self.env.var_decl(ident_token.value, type_token.value, None)

    def const_decl(self, tree: Tree):
        ident_token: Token = tree.children[0]
        expr_tree: Tree | Token = tree.children[1]
        value = self.eval_expr(expr_tree)
        self.env.const_decl(ident_token.value, value) 


    def assign(self, tree: Tree):
        # Pattern: IDENT ARROW expr (arrow token is ignored)
        name_token: Token = tree.children[0]
        name = name_token.value
        expr_tree: Tree | Token = tree.children[-1]  # last child is the expression
        value = self.eval_expr(expr_tree)
        self.env.set(name, value)
        # TODO: check type of variable and value

    # I/O ------------------------------------------------------------------

    def input(self, tree: Tree):  # noqa: D401  (imperative form)
        name_token: Token = tree.children[0]
        name = name_token.value
        user_val = input(f"INPUT {name}: ")
        expected_type = self.env.get_type(name)

        def _cast(val: str, t: str):
            try:
                if t == "INTEGER":
                    return int(val)
                if t == "REAL":
                    return float(val)
                if t == "BOOLEAN":
                    if val.strip().upper() in {"TRUE", "FALSE"}:
                        return val.strip().upper() == "TRUE"
                    raise ValueError
                if t == "CHAR":
                    if len(val) != 1:
                        raise ValueError
                    return val
            except ValueError:
                raise ValueError(f"Cannot convert '{val}' to {t}") from None
            return val  # STRING / DATE and default

        cast_val: object
        try:
            cast_val = _cast(user_val, expected_type)
        except ValueError as exc:
            print(exc)
            return
        self.env.set(name, cast_val)

    def output(self, tree: Tree):
        values: list[object] = []

        def collect(node: Tree | Token):
            if isinstance(node, Tree) and node.data == 'output_list':
                for child in node.children:
                    if isinstance(child, Token) and child.value == ',':
                        continue
                    collect(child)
            else:
                values.append(self.eval_expr(node))

        for child in tree.children:
            collect(child)

        print(*values)

    # Control flow ---------------------------------------------------------

    def if_no_else(self, tree: Tree):
        cond_tree = tree.children[0]
        if self.eval_expr(cond_tree):
            for stmt in tree.children[1:]:
                self.visit(stmt)

    def if_else(self, tree: Tree):
        cond_tree = tree.children[0]
        # The grammar produces THEN statements first until an 'ELSE' marker
        # We detect the split by finding the Tree labeled 'else_block' if it exists,
        # otherwise we approximate by half-splitting – good enough for skeleton.
        then_block: list[Tree] = []
        else_block: list[Tree] = []
        in_else = False
        for child in tree.children[1:]:
            if isinstance(child, Token) and child.type == "ELSE":  # unlikely but safe-guard
                in_else = True
                continue
            (else_block if in_else else then_block).append(child)
        target_block = then_block if self.eval_expr(cond_tree) else else_block
        for stmt in target_block:
            self.visit(stmt)

    def while_stmt(self, tree: Tree):
        cond_tree = tree.children[0]
        body = tree.children[1:]
        while self.eval_expr(cond_tree):
            for stmt in body:
                self.visit(stmt)

    def for_loop(self, tree: Tree):
        """Execute a FOR loop. Children layout (tokens + subtrees):
        IDENT, ARROW, start_expr, "TO", end_expr, ["STEP", step_expr], body..., "NEXT", IDENT
        """
        children = list(tree.children)

        var_name = children[0].value  # IDENT

        # Extract start & end expressions
        start_expr = children[2]  # after ARROW token
        end_expr_index = 4  # Ident (0), arrow (1), start (2), TO (3), end_expr (4)
        end_expr = children[end_expr_index]

        cursor = end_expr_index + 1  # points to token after end_expr

        # Optional STEP
        step = 1
        if cursor < len(children) and isinstance(children[cursor], Token) and children[cursor].type == "STEP":
            step_expr = children[cursor + 1]
            step = self.eval_expr(step_expr)
            cursor += 2

        # The body is until the last "NEXT" token (penultimate child)
        body = children[cursor:-2]  # skip "NEXT" and closing IDENT

        idx = self.eval_expr(start_expr)
        end_val = self.eval_expr(end_expr)

        # Initialise loop variable
        if var_name in self.env:
            self.env.set(var_name, idx)
        else:
            self.env.var_decl(var_name, idx)

        # Loop execution
        def continue_condition(current: int | float) -> bool:
            return (step > 0 and current <= end_val) or (step < 0 and current >= end_val)

        while continue_condition(self.env.get(var_name)):
            for stmt in body:
                self.visit(stmt)
            self.env.set(var_name, self.env.get(var_name) + step)

    # ---------------------------------------------------------------------
    # Expression evaluation (helper, not a grammar rule)
    # ---------------------------------------------------------------------

    def eval_expr(self, node: Tree | Token):  # noqa: C901 (complexity fine for skeleton)
        if isinstance(node, Token):
            match node.type:
                case "NUMBER":
                    return int(node) if node.value.isdigit() else float(node)
                case "STRING":
                    return node.value.strip("\"")
                case "IDENT":
                    return self.env.get(node.value)
            raise ValueError(f"Unsupported token: {node}")

        if not isinstance(node, Tree):
            raise TypeError(f"Expected Tree/Token, got {type(node)}")

        # Map node.data to operations
        op = node.data
        if op in {"add", "sub", "mul", "div", "int_div", "mod", "and_op", "or_op"}:
            a = self.eval_expr(node.children[0])
            b = self.eval_expr(node.children[1])
            return {
                "add": a + b,
                "sub": a - b,
                "mul": a * b,
                "div": a / b,
                "int_div": a // b,
                "mod": a % b,
                "and_op": bool(a) and bool(b),
                "or_op": bool(a) or bool(b),
            }[op]
        if op == "compare":
            if len(node.children) == 1:
                return self.eval_expr(node.children[0])
            left_val = self.eval_expr(node.children[0])
            op_token = node.children[1]
            right_val = self.eval_expr(node.children[2])
            return self._compare_values(op_token, left_val, right_val)
        if op == "neg":
            return -self.eval_expr(node.children[0])
        if op == "not_op":
            return not self.eval_expr(node.children[0])
        if op == "number":
            return self.eval_expr(node.children[0])
        if op in {"var", "string"}:
            return self.eval_expr(node.children[0])

        # Fallback: evaluate all children to force visiting
        for child in node.children:
            self.eval_expr(child)
        return None

    # ------------------------------------------------------------------

    @staticmethod
    def _compare_values(op_token: Token | Tree, a: object, b: object) -> bool:
        """Return the result of a <op_token> b for the supported operators."""
        if not isinstance(op_token, Token):
            return False
        op = op_token.value
        match op:
            case "=":
                return a == b
            case "<>":
                return a != b
            case "<":
                return a < b
            case ">":
                return a > b
            case "<=":
                return a <= b
            case ">=":
                return a >= b
        raise ValueError(f"Unknown comparator {op}") 