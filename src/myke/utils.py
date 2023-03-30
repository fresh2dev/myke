from __future__ import annotations

import os
import re
import stat
from importlib.machinery import SourceFileLoader
from pathlib import Path
from shutil import which
from subprocess import DEVNULL, CalledProcessError, CompletedProcess, run
from typing import Any

from yapx.utils import convert_to_command_string

__all__ = [
    "convert_to_command_string",
    "make_executable",
    "is_version",
    "get_repo_root",
]


def split_and_trim_text(txt: str | None) -> list[str]:
    if txt is None:
        return []

    txt = txt.strip()

    if not txt:
        return []

    return [x_trim for x in txt.splitlines() for x_trim in [x.strip()] if x_trim]


def make_executable(file: str) -> None:
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IEXEC)


def is_version(txt: str) -> bool:
    # https://github.com/pypa/packaging/blob/main/packaging/version.py
    VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""
    return (
        re.compile(f"^{VERSION_PATTERN}$", flags=re.VERBOSE | re.IGNORECASE).search(txt)
        is not None
    )


def get_repo_root(path: str | Path | None = None) -> Path | None:
    if not which("git"):
        return None

    if path is None:
        path = Path.cwd()
    elif not isinstance(path, Path):
        path = Path(path)

    if path is None:
        path = Path.cwd()
    elif not isinstance(path, Path):
        path = Path(path)

    try:
        run(
            ["git", "status", "--porcelain"],
            stdout=DEVNULL,
            stderr=DEVNULL,
            cwd=path,
            check=True,
        )
    except CalledProcessError:
        return None

    p: CompletedProcess = run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )

    return Path(p.stdout.strip())


class _MykeSourceFileLoader(SourceFileLoader):
    """SourceFileLoader that does not output '__pycache__'"""

    def _cache_bytecode(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()

    def set_data(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()
