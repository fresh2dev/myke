"""> Functions for printing."""

import collections.abc
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from ..globals import MYKE_VAR_NAME, TASKS


class echo:
    def __new__(cls, *args: Any, **kwargs: Any) -> None:  # type: ignore
        cls.text(*args, **kwargs)

    @staticmethod
    def _print(*args: Any, print_kwargs: Optional[Dict[str, Any]] = None) -> None:
        if not print_kwargs:
            print_kwargs = {}
        print(*args, **print_kwargs)

    @classmethod
    def text(cls, *args: Any, **kwargs: Any) -> None:
        """Prints text.

        Equivalent to base `print` command; only exists for consistency.

        Arguments:
            *args:
            **kwargs:

        Examples:
            >>> import myke
            ...
            >>> myke.echo.text('Hello World.')
            Hello World.
        """
        cls._print(*args, print_kwargs=kwargs)

    @classmethod
    def lines(
        cls,
        seq: Sequence[Optional[str]],
        linesep: str = os.linesep,
        print_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Prints lines of text.

        Arguments:
            seq: lines of text to print.
            linesep: line separator.
            print_kwargs: kwargs passed to `print`.

        Examples:
            >>> import myke
            ...
            >>> myke.echo.lines(['Hello World.', 'Goodbye World.'])
            Hello World.
            Goodbye World.
        """
        cls._print(linesep.join([str(x) for x in seq]), print_kwargs=print_kwargs)

    @classmethod
    def json(
        cls,
        obj: Any,
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Prints a dictionary as a JSON string.

        Arguments:
            obj: object to convert to JSON and print.
            print_kwargs: kwargs passed to `print`.
            **kwargs: kwargs passed to `json.dumps`.

        Examples:
            >>> import myke
            ...
            >>> myke.echo.json(
            ...     {'Messages': ['Hello World.', 'Goodbye World.']},
            ...     indent=4,
            ... )
            {
                "Messages": [
                    "Hello World.",
                    "Goodbye World."
                ]
            }
        """
        import json as _json

        cls._print(_json.dumps(obj, **kwargs), print_kwargs=print_kwargs)

    @classmethod
    def table(
        cls,
        obj: Union[Iterable[Iterable[Any]], Mapping[str, Iterable[Any]]],
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Prints a dictionary as a table.

        Arguments:
            obj: list of dicts print.
            print_kwargs: kwargs passed to `print`.
            **kwargs: kwargs passed to `tabulate`.

        Examples:
            >>> import myke
            ...
            >>> myke.echo.table([
            ...     {'row': 1, 'Message': 'Hello World.'},
            ...     {'row': 2, 'Message': 'Goodbye World.'},
            ... ])
              row  Message
            -----  --------------
                1  Hello World.
                2  Goodbye World.
        """
        from tabulate import tabulate

        if (
            obj
            and isinstance(obj, collections.abc.Sequence)
            and isinstance(obj[0], dict)
            and "headers" not in kwargs
        ):
            kwargs["headers"] = "keys"

        cls._print(tabulate(obj, **kwargs), print_kwargs=print_kwargs)

    @classmethod
    def pretty(
        cls,
        obj: Any,
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Pretty-print objects.

        Arguments:
            obj: object to print.
            print_kwargs: kwargs passed to `print`.
            **kwargs: kwargs passed to `pprint.pformat`.

        Examples:
            >>> import myke
            ...
            >>> myke.echo.pretty('Hello World.')
            'Hello World.'
        """
        from pprint import pformat

        cls._print(pformat(obj, **kwargs), print_kwargs=print_kwargs)

    @classmethod
    def tasks(cls, prog: Optional[str] = None, tablefmt: Optional[str] = None) -> None:
        """Print a table of registered myke tasks.

        Args:
            tablefmt: table format to use (from `tabulate`)

        Examples:
            >>> import myke
            ...
            >>> @myke.task  # doctest: +SKIP
            ... def say_hello(name):
            ...     print(f"Hello {name}.")
            ...
            >>> @myke.task  # doctest: +SKIP
            ... def say_goodbye(name):
            ...     print(f"Goodbye {name}.")
            >>> myke.echo.tasks()
            <BLANKLINE>
            ===========  ==========
            Task         Source
            ===========  ==========
            say-goodbye  myke.tasks
            say-hello    myke.tasks
            ===========  ==========
            <BLANKLINE>
            To view task parameters, see:
            > myke <task-name> --help
            <BLANKLINE>
        """
        cls.text()

        if not TASKS:
            cls.text("No tasks found.")
        else:
            records: List[Dict[str, str]] = [
                {"Task": k, "Source": v.__module__} for k, v in sorted(TASKS.items())
            ]

            if not prog:
                prog = MYKE_VAR_NAME

            try:
                if not tablefmt:
                    tablefmt = "rst"
                echo.table(records, tablefmt=tablefmt)
            except ModuleNotFoundError:
                cls.text("TASKS")
                cls.text("-----")
                cls.lines([str(x) if x else "" for x in records])

            cls.text()
            cls.text("To view task parameters, see:")
            cls.text(f"> {prog} <task-name> --help")

        cls.text()
