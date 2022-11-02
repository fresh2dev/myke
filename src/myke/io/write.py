import os
from typing import Any, List, Optional, Union

from ..io import read
from ..main import DEFAULT_MYKEFILE
from ..utils import make_executable


def text(
    content: Union[str, bytes],
    path: str,
    append: bool = False,
    overwrite: bool = False,
    **kwargs: Any
) -> None:
    mode_default: str = "w"

    mode: str = kwargs.pop("mode", mode_default)

    if os.path.exists(path):
        if overwrite:
            os.remove(path)
        elif append and mode == mode_default:
            mode = "a"
        else:
            raise FileExistsError(path)

    if mode == mode_default:
        if isinstance(content, bytes):
            mode += "b"

        if not os.path.exists(path):
            mode += "+"

    with open(path, mode=mode, **kwargs) as f:
        f.write(content)


def lines(
    content: List[str],
    path: str,
    append: bool = False,
    overwrite: bool = False,
    **kwargs: Any
) -> None:
    if isinstance(content, str):
        raise TypeError("expected a list of strings, not a string")
    text(
        path=path,
        content=os.linesep.join(content),
        append=append,
        overwrite=overwrite,
        **kwargs
    )


def mykefile(path: Optional[str] = None) -> None:
    if not path:
        path = os.getcwd()

    if os.path.isdir(path):
        path = os.path.join(path, DEFAULT_MYKEFILE)

    text(
        path=path,
        content="""#!/usr/bin/env python3
# type: ignore

import myke


@myke.task(root=True)
def setup() -> None:
    print("charging lazer beamz")


@myke.task
def print_hello(
    name = myke.arg(default="world", env_var="HELLO_NAME", flags=["-n", "--name"])
):
    print(f"hello {name}")

@myke.task_sh
def echo_hello(
    name = myke.arg(default="world", env_var="HELLO_NAME", flags=["-n", "--name"])
):
    return f"echo 'hello {name}'"

if __name__ == "__main__":
    myke.main(__file__)
""",
    )

    make_executable(path)


def url(
    addr: str,
    path: Optional[str] = None,
    append: bool = False,
    overwrite: bool = False,
    **kwargs: Any
) -> str:
    if not path:
        path = os.getcwd()

    if os.path.isdir(path):
        path = os.path.join(path, os.path.basename(addr))

    resp: str = read.url(addr)

    text(content=resp, path=path, append=append, overwrite=overwrite, **kwargs)

    return path
