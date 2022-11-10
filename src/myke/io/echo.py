import collections.abc
import os
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Union


class echo:
    def __new__(self, txt: Optional[str] = None, **kwargs: Any) -> None:
        self.text(txt, **kwargs)

    @staticmethod
    def _print(txt: str, print_kwargs: Optional[Dict[str, Any]] = None) -> None:
        if not print_kwargs:
            print_kwargs = {}
        print(txt, **print_kwargs)

    @classmethod
    def text(cls, txt: Optional[str] = None, **kwargs: Any) -> None:
        args = [txt] if txt is not None else []
        cls._print(*args, kwargs)

    @classmethod
    def lines(
        cls,
        seq: Sequence[str],
        linesep: str = os.linesep,
        print_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        cls._print(linesep.join(seq), print_kwargs)

    @classmethod
    def json(
        cls, obj: Any, print_kwargs: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        import json as _json

        cls._print(_json.dumps(obj, **kwargs), print_kwargs)

    @classmethod
    def table(
        cls,
        obj: Union[Iterable[Iterable[Any]], Mapping[str, Iterable[Any]]],
        print_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        from tabulate import tabulate

        if (
            obj
            and isinstance(obj, collections.abc.Sequence)
            and isinstance(obj[0], dict)
            and "headers" not in kwargs
        ):
            kwargs["headers"] = "keys"

        cls._print(tabulate(obj, **kwargs), print_kwargs)

    @classmethod
    def pretty(
        cls, obj: Any, print_kwargs: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        from pprint import pformat

        cls._print(pformat(obj, **kwargs), print_kwargs)
