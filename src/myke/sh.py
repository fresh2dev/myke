from __future__ import annotations

import json
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
        shell = isinstance(args, str) and " " in args

    env = env.copy() if env else os.environ.copy()

    if env_update:
        for k, v in env_update.items():
            if v is None:
                env.pop(k)
            else:
                env[k] = v

    if not echo and not capture_output:
        for k in ("stdout", "stderr"):
            kwargs[k] = subprocess.DEVNULL

    p: subprocess.CompletedProcess[str] = subprocess.run(
        args,
        shell=shell,
        env=env,
        cwd=cwd,
        timeout=timeout,
        capture_output=bool(capture_output),
        text=capture_output,
        check=False,
        **kwargs,
    )

    if echo and capture_output:
        for out in (p.stdout, p.stderr):
            if out:
                print(out.rstrip(os.linesep))

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


def _run_pip(
    *args: str,
    pip_args: list[str] | None = None,
    echo: bool = False,
    capture_output: bool = False,
    **kwargs: str,
) -> tuple[str | None, str | None, int]:
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
    )


def require(
    *args: str,
    pip_args: list[str] | None = None,
    skip_check: bool = False,
    **kwargs: str,
) -> tuple[str | None, str | None, int]:
    if not pip_args:
        pip_args = []

    dry_run_args: list[str] = (
        [] if skip_check else ["-qq", "--dry-run", "--report", "-"]
    )

    stdout, stderr, returncode = _run_pip(
        *args,
        pip_args=pip_args + dry_run_args,
        echo=False,
        capture_output=True,
        **kwargs,
    )

    if dry_run_args:
        if not stdout or returncode != 0:
            print(stdout, stderr, returncode)
            return stdout, stderr, returncode

        result: dict[str, Any] = json.loads(stdout)

        if result and result.get("install"):
            return _run_pip(
                *args,
                pip_args=pip_args,
                echo=True,
                capture_output=False,
                **kwargs,
            )

    return stdout, stderr, returncode
