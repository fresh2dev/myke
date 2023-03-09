import os
from typing import Any, List, Optional, Union

from ..globals import DEFAULT_MYKEFILE
from ..io.read import read
from ..utils import make_executable


class write:
    def __new__(  # type: ignore
        cls,
        content: Union[str, bytes],
        path: str,
        append: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        cls.text(
            content=content,
            path=path,
            append=append,
            overwrite=overwrite,
            **kwargs,
        )

    @staticmethod
    def text(
        content: Union[str, bytes],
        path: str,
        append: bool = False,
        overwrite: bool = False,
        encoding: str = "utf-8",
        **kwargs: Any,
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

        with open(path, mode=mode, encoding=encoding, **kwargs) as f:
            f.write(content)

    @classmethod
    def lines(
        cls,
        content: List[Optional[str]],
        path: str,
        append: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        if isinstance(content, str):
            raise TypeError("expected a list of strings, not a string")
        cls.text(
            path=path,
            content=os.linesep.join([str(x) for x in content]),
            append=append,
            overwrite=overwrite,
            **kwargs,
        )

    @classmethod
    def mykefile(cls, path: Optional[str] = None) -> None:
        if not path:
            path = os.getcwd()

        if os.path.isdir(path):
            path = os.path.join(path, DEFAULT_MYKEFILE)

        cls.text(
            path=path,
            content="""#!/usr/bin/env python3
# type: ignore
# pylint: skip-file
# flake8: noqa
import myke  # noqa

myke.require(
    pip_args=[
        "--extra-index-url",
        "https://codeberg.org/api/packages/Fresh2dev/pypi/simple",
    ],
    mykefiles="0.0.1a3.dev44",
)
from mykefiles import hello_world  # noqa

# @myke.task(root=True)
# def setup():
#     # setup
#     ...
#
#     yield
#
#     # teardown
#     ...


if __name__ == "__main__":
    myke.main(__file__)
""",
        )

        make_executable(path)

    @classmethod
    def url(
        cls,
        addr: str,
        path: Optional[str] = None,
        append: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> str:
        if not path:
            path = os.getcwd()

        if os.path.isdir(path):
            path = os.path.join(path, os.path.basename(addr))

        resp: str = read.url(addr)

        cls.text(content=resp, path=path, append=append, overwrite=overwrite, **kwargs)

        return path
