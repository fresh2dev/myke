from __future__ import annotations

import collections.abc
import os
from functools import partial, wraps
from subprocess import CompletedProcess
from types import ModuleType
from typing import Any, Callable, Sequence

from .exceptions import MykeNotFoundError, NoTasksFoundError, TaskAlreadyRegisteredError
from .globals import MYKE_VAR_NAME, ROOT_TASK_KEY, TASKS
from .run import run, sh
from .utils import _MykeSourceFileLoader, convert_to_command_string


def add_tasks(*args: Callable[..., Any], **kwargs: Callable[..., Any]) -> None:
    kwargs.update({x.__name__: x for x in args})

    kwargs = {
        (ROOT_TASK_KEY if k == ROOT_TASK_KEY else convert_to_command_string(k)): v
        for k, v in kwargs.items()
    }

    for k, v in kwargs.items():
        v_existing: Callable[..., Any] | None = TASKS.get(k, None)
        if v_existing:
            raise TaskAlreadyRegisteredError(
                (
                    f"Failed to import module '{v.__module__}': "
                    f"Task '{k}' already defined from module '{v_existing.__module__}'"
                ),
            )
        TASKS[k] = v


def import_mykefile(path: str) -> None:
    n_tasks_before: int = len(TASKS)

    loader = _MykeSourceFileLoader(os.path.relpath(path), path)
    mod: ModuleType = ModuleType(loader.name)
    loader.exec_module(mod)

    if not hasattr(mod, MYKE_VAR_NAME):
        raise MykeNotFoundError(path)

    if len(TASKS) <= n_tasks_before:
        raise NoTasksFoundError(path)


def import_module(name: str) -> None:
    n_tasks_before: int = len(TASKS)

    __import__(name)

    if len(TASKS) <= n_tasks_before:
        raise NoTasksFoundError(name)


def task(
    func: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    root: bool | None = False,
) -> Callable[..., Any] | Callable[..., Callable[..., Any]]:
    if not func:
        return partial(task, name=name, root=root)

    if root:
        name = ROOT_TASK_KEY

    if name:
        add_tasks(**{name: func})
    else:
        add_tasks(func)

    return func


def task_run(
    func: Callable[..., str | Sequence[str]] | None = None,
    *,
    name: str | None = None,
    root: bool | None = False,
    capture_output: bool | None = False,
    echo: bool | None = True,
    check: bool | None = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    env_update: dict[str, str | None] | None = None,
    timeout: float | None = None,
    executable: str | None = None,
) -> (
    Callable[..., CompletedProcess[bytes | str]]
    | Callable[..., Callable[..., CompletedProcess[bytes | str]]]
):
    if not func:
        return partial(
            task_sh,
            name=name,
            root=root,
            capture_output=capture_output,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

    @wraps(func)
    def _inner_func(*args: Any, **kwargs: Any) -> tuple[str | None, str | None, int]:
        assert func

        func_script: str | Sequence[str] = func(*args, **kwargs)

        if not isinstance(func_script, str) and not isinstance(
            func_script,
            collections.abc.Sequence,
        ):
            raise TypeError(
                "Expected a string or list of strings to be returned for `sh` function",
            )

        return run(
            func_script,
            capture_output=capture_output,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

    if not name:
        name = func.__name__

    return task(_inner_func, name=name, root=root)


def task_sh(
    func: Callable[..., str | Sequence[str]] | None = None,
    *,
    name: str | None = None,
    root: bool | None = False,
    capture_output: bool | None = False,
    echo: bool | None = True,
    check: bool | None = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    env_update: dict[str, str | None] | None = None,
    timeout: float | None = None,
    executable: str | None = None,
) -> (
    Callable[..., CompletedProcess[bytes | str]]
    | Callable[..., Callable[..., CompletedProcess[bytes | str]]]
):
    if not func:
        return partial(
            task_sh,
            name=name,
            root=root,
            capture_output=capture_output,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

    @wraps(func)
    def _inner_func(*args: Any, **kwargs: Any) -> tuple[str | None, str | None, int]:
        assert func

        func_script: str = func(*args, **kwargs)

        if not isinstance(func_script, str) and not isinstance(
            func_script,
            collections.abc.Sequence,
        ):
            raise TypeError(
                "Expected a string to be returned for `sh` function",
            )

        return sh(
            func_script,
            capture_output=capture_output,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

    if not name:
        name = func.__name__

    return task(_inner_func, name=name, root=root)
