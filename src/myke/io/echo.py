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
        cls._print(*args, print_kwargs=kwargs)

    @classmethod
    def lines(
        cls,
        seq: Sequence[Optional[str]],
        linesep: str = os.linesep,
        print_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        cls._print(linesep.join([str(x) for x in seq]), print_kwargs=print_kwargs)

    @classmethod
    def json(
        cls,
        obj: Any,
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        import json as _json

        cls._print(_json.dumps(obj, **kwargs), print_kwargs=print_kwargs)

    @classmethod
    def table(
        cls,
        obj: Union[Iterable[Iterable[Any]], Mapping[str, Iterable[Any]]],
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
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
        from pprint import pformat

        cls._print(pformat(obj, **kwargs), print_kwargs=print_kwargs)

    @classmethod
    def tasks(cls, prog: Optional[str] = None, tablefmt: Optional[str] = None) -> None:
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
