__all__ = ["sh", "sh_stdout", "sh_stdout_lines"]

import os
import subprocess
from functools import wraps
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .exceptions import CalledProcessError
from .utils import split_and_trim_text


def sh(
    args: Union[str, Sequence[str]],
    capture_output: Optional[bool] = False,
    echo: Optional[bool] = True,
    check: Optional[bool] = True,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    env_update: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    **kwargs: Any,
) -> Tuple[Optional[str], Optional[str], int]:

    kwargs["args"] = args
    kwargs["cwd"] = cwd
    kwargs["timeout"] = timeout
    kwargs["check"] = False
    kwargs["shell"] = True
    kwargs["text"] = True
    kwargs["capture_output"] = capture_output

    if env:
        env = env.copy()
    else:
        env = os.environ.copy()

    if env_update:
        env.update(env_update)

    kwargs["env"] = env

    p: subprocess.CompletedProcess = subprocess.run(**kwargs)
    assert isinstance(p, subprocess.CompletedProcess)

    if capture_output and echo:
        if p.stdout:
            print(p.stdout.rstrip(os.linesep))
        if p.stderr:
            print(p.stderr.rstrip(os.linesep))

    if check and p.returncode:
        raise CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)

    return p.stdout, p.stderr, p.returncode


@wraps(sh)
def sh_stdout_lines(*args: Any, **kwargs: Any) -> List[str]:
    kwargs["capture_output"] = True
    kwargs["echo"] = kwargs.get("echo", False)
    stdout, *_ = sh(*args, **kwargs)
    return split_and_trim_text(stdout)


@wraps(sh)
def sh_stdout(*args: Any, **kwargs: Any) -> str:
    return os.linesep.join(sh_stdout_lines(*args, **kwargs))
