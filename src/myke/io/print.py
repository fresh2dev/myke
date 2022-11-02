import collections.abc
import os
from functools import wraps
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Union


def text(txt: Optional[str] = None, **kwargs: Any) -> None:
    args = [txt] if txt else []
    print(*args, **kwargs)


@wraps(text)
def _print(txt: str, print_kwargs: Optional[Dict[str, Any]] = None) -> None:
    if not print_kwargs:
        print_kwargs = {}
    print(txt, **print_kwargs)


def lines(
    seq: Sequence[str],
    linesep: str = os.linesep,
    print_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    _print(linesep.join(seq), print_kwargs)


def json(
    obj: Any, print_kwargs: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> None:
    import json as _json

    _print(_json.dumps(obj, **kwargs), print_kwargs)


def table(
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

    _print(tabulate(obj, **kwargs), print_kwargs)


def pretty(
    obj: Any, print_kwargs: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> None:
    from pprint import pformat

    _print(pformat(obj, **kwargs), print_kwargs)
