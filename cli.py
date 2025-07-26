from __future__ import annotations

import sys
from pathlib import Path

from lark import Lark

from cie_runtime import Environment, Evaluator


GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: cie-run <source_file>")
        raise SystemExit(1)

    source_path = Path(sys.argv[1])
    if not source_path.exists():
        print(f"File not found: {source_path}")
        raise SystemExit(1)

    source_code = source_path.read_text(encoding="utf-8")

    parser = Lark.open(str(GRAMMAR_PATH), parser="lalr", start="start")
    tree = parser.parse(source_code)

    env = Environment()
    evaluator = Evaluator(env)
    evaluator.visit(tree)


if __name__ == "__main__":
    main() 