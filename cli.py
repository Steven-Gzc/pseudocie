#!/usr/bin/env python
"""Minimal command-line runner for CIE A-Level pseudocode files.

Usage
-----
python cli.py hello.cie           # run program, no extras
python cli.py hello.cie -t        # additionally print parse tree
python cli.py hello.cie -e        # print environment after run
python cli.py hello.cie -d        # dump tree to tests/<name>.tree.txt

For convenience you can also install an editable copy of this repo and
create a console-script entry-point (e.g. ``cie-run``). Until then this
script works with a plain interpreter call.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from parse_utils import parse_file
from cie_runtime import run


def _positive_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {path_str}")
    return path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cie-run",
        description="Run a CIE A-Level pseudocode program ( .cie file )",
    )
    p.add_argument("source", type=_positive_path, help="Path to .cie source file")
    p.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the parse tree to stdout before execution.",
    )
    p.add_argument(
        "-d",
        "--dump-tree",
        action="store_true",
        help="Dump the tree to tests/<stem>.tree.txt like parse_utils does.",
    )
    p.add_argument(
        "-e",
        "--env",
        action="store_true",
        help="Print the final environment after execution.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    # Parse source
    tree = parse_file(
        args.source,
        show_tree=args.tree,
        save_tree=args.dump_tree,
    )

    # Execute program
    env = run(tree)

    if args.env:
        print("\nFinal environment:\n" + "-" * 20)
        print(env)


if __name__ == "__main__":
    main(sys.argv[1:]) 