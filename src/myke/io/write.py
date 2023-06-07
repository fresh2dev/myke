"""> Functions for writing."""

import os
from pathlib import Path
from typing import Any, List, Optional, Union

from ..globals import DEFAULT_MYKEFILE
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
        path: Union[str, Path],
        append: bool = False,
        overwrite: bool = False,
        encoding: str = "utf-8",
        **kwargs: Any,
    ) -> None:
        """Write text to a file.

        Args:
            content:
            path:
            append:
            overwrite:
            encoding:

        Raises:
            FileExistsError: if file exists and overwrite is False.


        Examples:
            >>> import myke
            ...
            >>> myke.write.text('hello world', '/path/to/file.txt')  # doctest: +SKIP
        """
        mode_default: str = "w"

        mode: str = kwargs.pop("mode", mode_default)

        if isinstance(path, str):
            path = Path(path)

        if path.exists():
            if overwrite:
                path.unlink()
            elif append and mode == mode_default:
                mode = "a"
            else:
                raise FileExistsError(path)

        if mode == mode_default:
            if isinstance(content, bytes):
                mode += "b"

            if not path.exists():
                mode += "+"

        with path.open(mode=mode, encoding=encoding, **kwargs) as f:
            f.write(content)

    @classmethod
    def lines(
        cls,
        content: List[Optional[str]],
        path: Union[str, Path],
        append: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write lines of text to a file.

        Args:
            content:
            path:
            append:
            overwrite:

        Raises:
            FileExistsError: if file exists and overwrite is False.


        Examples:
            >>> import myke
            ...
            >>> myke.write.text(['hello', 'world'], '/path/to/file.txt')  # doctest: +SKIP
        """
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
    def mykefile(
        cls,
        path: Union[None, str, Path] = None,
    ) -> None:
        """Create a new Mykefile.

        Args:
            path:

        Raises:
            FileExistsError: if file exists and overwrite is False.


        Examples:
            >>> import myke
            ...
            >>> myke.write.mykefile('/path/to/Mykefile')  # doctest: +SKIP
        """
        if not path:
            path = Path.cwd()
        elif isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            path = path / DEFAULT_MYKEFILE

        cls.text(
            path=path,
            content=r"""from myke import task, shell_task

@task(root=True)
def setup():
    # setup
    ...

    yield

    # teardown
    ...

@task
def do_work():
    ...

@shell_task
def more_work():
    return 'echo ...'
""",
        )

        make_executable(path)
