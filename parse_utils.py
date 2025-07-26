from __future__ import annotations

from pathlib import Path
from typing import Final

from lark import Lark, Tree

# Path to the grammar file relative to project root
_GRAMMAR_PATH: Final[Path] = Path(__file__).with_name("grammar.lark")


def parse_code(source_code: str, *, show_tree: bool = True) -> Tree:
    """Parse *source_code* (CIE pseudocode) and return the Lark parse tree.

    Parameters
    ----------
    source_code : str
        The raw pseudocode to parse.
    show_tree : bool, default True
        Pretty-print the tree to stdout after parsing.
    """
    parser = Lark.open(str(_GRAMMAR_PATH), parser="lalr", start="start")
    tree = parser.parse(source_code)

    if show_tree:
        print(tree.pretty())

    return tree


def _tree_output_path(source_file: Path) -> Path:
    """Return path in tests/ dir where the pretty tree should be dumped."""
    tests_dir = Path(__file__).with_name("tests")
    tests_dir.mkdir(exist_ok=True)
    return tests_dir / f"{source_file.stem}.tree.txt"


def parse_file(file_path: str | Path, *, show_tree: bool = True, save_tree: bool = True) -> Tree:
    """Parse a pseudocode *file* and optionally persist the pretty tree.

    Parameters
    ----------
    file_path : str | Path
        Path to the .cie pseudocode file.
    show_tree : bool, default True
        Pretty-print tree to stdout.
    save_tree : bool, default True
        If True, dumps the pretty representation to tests/<stem>.tree.txt
    """
    src_path = Path(file_path)
    tree = parse_code(src_path.read_text(encoding="utf-8"), show_tree=show_tree)

    if save_tree:
        out_path = _tree_output_path(src_path)
        out_path.write_text(tree.pretty(), encoding="utf-8")
    return tree


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parse_utils.py <source_file>")
        raise SystemExit(1)

    parse_file(sys.argv[1]) 