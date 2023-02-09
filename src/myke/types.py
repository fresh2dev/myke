from __future__ import annotations

import sys
from typing import Callable

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class MykeType(Protocol):
    TASKS: dict[str, Callable[..., None]]
