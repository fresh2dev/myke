from __future__ import annotations

from typing import Callable

from yapx.types import Annotated  # pylint: disable=unused-import # noqa: F401
from yapx.types import Literal  # pylint: disable=unused-import # noqa: F401
from yapx.types import Protocol  # pylint: disable=unused-import # noqa: F401

__all__ = ["Annotated", "Literal", "Protocol", "MykeType"]


class MykeType(Protocol):
    TASKS: dict[str, Callable[..., None]]
