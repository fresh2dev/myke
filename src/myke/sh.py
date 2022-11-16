from __future__ import annotations

import os
import subprocess
import sys
from functools import wraps
from typing import Any, Sequence

from .exceptions import CalledProcessError
from .utils import split_and_trim_text

__all__ = ["sh", "sh_stdout", "sh_stdout_lines"]


def sh(
    args: str | Sequence[str],
    capture_output: None | bool = False,
    echo: bool | None = True,
    check: bool | None = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    env_update: dict[str, str] | None = None,
    timeout: float | None = None,
    **kwargs: Any,
) -> tuple[str | None, str | None, int]:

    kwargs["cwd"] = cwd
    kwargs["timeout"] = timeout
    kwargs["shell"] = kwargs.get("shell", True)
    kwargs["capture_output"] = capture_output
    kwargs["text"] = True

    if env:
        env = env.copy()
    else:
        env = os.environ.copy()

    if env_update:
        env.update(env_update)

    kwargs["env"] = env

    p: subprocess.CompletedProcess[str] = subprocess.run(args, check=False, **kwargs)

    if capture_output and echo:
        if p.stdout:
            print(p.stdout.rstrip(os.linesep))
        if p.stderr:
            print(p.stderr.rstrip(os.linesep))

    if check and p.returncode:
        raise CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)

    return p.stdout, p.stderr, p.returncode


@wraps(sh)
def sh_stdout_lines(*args: Any, **kwargs: Any) -> list[str]:
    kwargs["capture_output"] = True
    kwargs["echo"] = kwargs.get("echo", False)
    stdout, *_ = sh(*args, **kwargs)
    return split_and_trim_text(stdout)


@wraps(sh)
def sh_stdout(*args: Any, **kwargs: Any) -> str:
    return os.linesep.join(sh_stdout_lines(*args, **kwargs))
