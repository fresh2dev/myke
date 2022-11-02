from typing import Callable, Dict

try:
    from typing_extensions import Protocol
except ImportError:
    from typing import Protocol


class MykeType(Protocol):
    TASKS: Dict[str, Callable[..., None]]
