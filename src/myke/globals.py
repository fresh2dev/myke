from __future__ import annotations

from typing import Callable

TASKS: dict[str, Callable[..., None]] = {}

MYKE_VAR_NAME: str = "myke"

DEFAULT_MYKEFILE: str = "Mykefile"

ROOT_TASK_KEY: str = "__root__"
