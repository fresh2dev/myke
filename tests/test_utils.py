from pathlib import Path
from typing import List

import myke


def test_split_and_trim_text():
    in_str: str = "  \n\n one \n\n  two  \n three\n\n\n four five"
    out_list: List[str] = ["one", "two", "three", "four five"]
    assert myke.utils.split_and_trim_text(in_str) == out_list


def test_is_version():
    assert myke.utils.is_version("0.0.1a1.dev0")
    assert myke.utils.is_version("v0.0.1a1.dev0")
    assert not myke.utils.is_version("wat0.0.1a1.dev0")


def test_get_repo_root():
    assert (
        myke.utils.get_repo_root()
        == myke.utils.get_repo_root(Path.cwd() / "README.md")
        == myke.utils.get_repo_root(Path.cwd() / ".git")
        == myke.utils.get_repo_root(
            Path.cwd() / ".git" / "refs" / "heads" / "main",
        )
    )
