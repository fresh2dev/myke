from __future__ import annotations

import os
import subprocess
import sys
from functools import wraps
from typing import Any, Sequence

from .exceptions import CalledProcessError
from .utils import split_and_trim_text

__all__ = ["run", "sh", "sh_stdout", "sh_stdout_lines", "require"]


def run(
    args: str | Sequence[str],
    capture_output: None | bool = False,
    echo: bool | None = True,
    check: bool | None = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    env_update: dict[str, str] | None = None,
    timeout: float | None = None,
    shell: bool | None = None,
    **kwargs: Any,
) -> tuple[str | None, str | None, int]:
    if shell is None:
        shell = isinstance(args, str)

    kwargs["cwd"] = cwd
    kwargs["timeout"] = timeout
    kwargs["capture_output"] = capture_output
    kwargs["text"] = True

    if env:
        env = env.copy()
    else:
        env = os.environ.copy()

    if env_update:
        for k, v in env_update.items():
            if v is None:
                env.pop(k)
            else:
                env[k] = v

    kwargs["env"] = env

    p: subprocess.CompletedProcess[str] = subprocess.run(
        args, shell=shell, check=False, **kwargs
    )

    if capture_output and echo:
        if p.stdout:
            print(p.stdout.rstrip(os.linesep))
        if p.stderr:
            print(p.stderr.rstrip(os.linesep))

    if check and p.returncode:
        raise CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)

    return p.stdout, p.stderr, p.returncode


@wraps(run)
def sh(*args: Any, **kwargs: Any) -> tuple[str | None, str | None, int]:
    kwargs["shell"] = True
    return run(*args, **kwargs)


@wraps(sh)
def sh_stdout_lines(*args: Any, **kwargs: Any) -> list[str]:
    kwargs["capture_output"] = True
    kwargs["echo"] = kwargs.get("echo", False)
    stdout, *_ = sh(*args, **kwargs)
    return split_and_trim_text(stdout)


@wraps(sh)
def sh_stdout(*args: Any, **kwargs: Any) -> str:
    return os.linesep.join(sh_stdout_lines(*args, **kwargs))


def require(*args: str, pip_args: list[str] | None = None, **kwargs: str) -> None:
    if not pip_args:
        pip_args = []

    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *pip_args,
            *args,
            *[f"{k}=={v}" for k, v in kwargs.items()],
        ],
        echo=False,
        capture_output=False,
    )
