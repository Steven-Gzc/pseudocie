from __future__ import annotations

import sys
from pathlib import Path

from lark import Lark, Tree


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = REPO_ROOT / "grammar.lark"


def parse_source(source_code: str, *, show_tree: bool = True) -> Tree:  # noqa: D401
    """Parse *source_code* using the project grammar and return the parse tree.

    Parameters
    ----------
    source_code : str
        Raw CIE-pseudocode text to parse.
    show_tree : bool, default True
        Pretty-print the resulting tree when *True* (console aid).
    """
    parser = Lark.open(str(GRAMMAR_PATH), parser="lalr", start="start")
    tree = parser.parse(source_code)

    if show_tree:
        print(tree.pretty())

    return tree


# ---------------------------------------------------------------------------
# CLI helper: python tests/parse_source.py [path_to_file]
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        code = file_path.read_text(encoding="utf-8")
    else:
        default_file = Path(__file__).with_name("expressions.cie")
        code = default_file.read_text(encoding="utf-8")
    parse_source(code) 