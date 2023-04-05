from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import wraps
from typing import Any, Sequence

from .utils import split_and_trim_text

__all__ = [
    "run",
    "run_stdout",
    "run_stdout_lines",
    "sh",
    "sh_stdout",
    "sh_stdout_lines",
    "require",
]


def run(
    args: str | Sequence[str],
    capture_output: None | bool = False,
    echo: bool | None = True,
    check: bool | None = True,
    env: dict[str, str] | None = None,
    env_update: dict[str, str | None] | None = None,
    shell: bool | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[bytes | str]:
    if shell is None:
        shell = isinstance(args, str) and " " in args

    env = env.copy() if env else os.environ.copy()

    if env_update:
        for k, v in env_update.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v

    if not echo and not capture_output:
        for k in ("stdout", "stderr"):
            kwargs[k] = subprocess.DEVNULL

    p: subprocess.CompletedProcess[str] = subprocess.run(
        args,
        shell=shell,
        env=env,
        capture_output=bool(capture_output),
        check=False,
        **kwargs,
    )

    try:
        if check:
            p.check_returncode()
    finally:
        if echo and capture_output:
            for x in (p.stdout, p.stderr):
                if x and isinstance(x, str):
                    print(x.rstrip(os.linesep))

    return p


@wraps(run)
def run_stdout_lines(*args: Any, **kwargs: Any) -> list[str]:
    kwargs["capture_output"] = True
    kwargs["text"] = True
    kwargs["echo"] = kwargs.get("echo", False)
    p: subprocess.CompletedProcess[str] = run(*args, **kwargs)
    return split_and_trim_text(p.stdout)


@wraps(run)
def run_stdout(*args: Any, **kwargs: Any) -> str:
    return os.linesep.join(run_stdout_lines(*args, **kwargs))


@wraps(run)
def sh(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes | str]:
    return run(*args, shell=True, **kwargs)


@wraps(sh)
def sh_stdout_lines(*args: Any, **kwargs: Any) -> list[str]:
    return run_stdout_lines(*args, shell=True, **kwargs)


@wraps(sh)
def sh_stdout(*args: Any, **kwargs: Any) -> str:
    return run_stdout(*args, shell=True, **kwargs)


def _run_pip(
    *args: str,
    pip_args: list[str] | None = None,
    echo: bool = False,
    capture_output: bool = False,
    **kwargs: str,
) -> subprocess.CompletedProcess[str]:
    if not pip_args:
        pip_args = []

    return run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *pip_args,
            *args,
            *[f"{k}=={v}" for k, v in kwargs.items()],
        ],
        echo=echo,
        capture_output=capture_output,
        text=True,
    )


def require(
    *args: str,
    pip_args: list[str] | None = None,
    skip_check: bool = False,
    **kwargs: str,
) -> subprocess.CompletedProcess[str]:
    if not pip_args:
        pip_args = []

    dry_run_args: list[str] = (
        [] if skip_check else ["-qq", "--dry-run", "--report", "-"]
    )

    p: subprocess.CompletedProcess[str] = _run_pip(
        *args,
        pip_args=pip_args + dry_run_args,
        echo=False,
        capture_output=True,
        **kwargs,
    )

    if dry_run_args:
        if not p.stdout or p.returncode != 0:
            print(p.stdout, p.stderr, p.returncode)
            return p

        result: dict[str, Any] = json.loads(p.stdout)

        if result and result.get("install"):
            return _run_pip(
                *args,
                pip_args=pip_args,
                echo=True,
                capture_output=False,
                **kwargs,
            )

    return p
