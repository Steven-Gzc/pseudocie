from __future__ import annotations

import sys
from pathlib import Path

from cie_runtime import Environment, Evaluator
from parse_utils import parse_file


USAGE = (
    "Usage: cie-run <source_file> [--tree]\n"
    "  --tree   Show parse tree on stdout while running"
)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(USAGE)
        raise SystemExit(1)

    # Collect args
    source_path = Path(sys.argv[1])
    show_tree = "--tree" in sys.argv[2:]

    if not source_path.exists():
        print(f"File not found: {source_path}")
        raise SystemExit(1)

    # Parse (also dumps tree into tests/ automatically)
    tree = parse_file(source_path, show_tree=show_tree, save_tree=True)

    # Evaluate
    env = Environment()
    evaluator = Evaluator(env)
    evaluator.visit(tree)


if __name__ == "__main__":
    main() 