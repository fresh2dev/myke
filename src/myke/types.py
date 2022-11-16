from __future__ import annotations

from typing import Callable

try:
    from typing_extensions import Protocol
except ImportError:
    from typing import Protocol


class MykeType(Protocol):
    TASKS: dict[str, Callable[..., None]]
