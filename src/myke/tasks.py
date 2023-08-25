"""> Functions for registering tasks with myke."""

from __future__ import annotations

import collections.abc
import os
from dataclasses import dataclass, field
from functools import partial, wraps
from subprocess import CompletedProcess
from types import ModuleType
from typing import Any, Callable, Sequence

import yapx

from .exceptions import NoTasksFoundError
from .run import sh
from .utils import _MykeSourceFileLoader, convert_to_command_string


@dataclass
class Task:
    name: str
    function: Callable[..., Any]
    parents: tuple[str | yapx.Command, ...] = field(default_factory=tuple)


TASKS: list[Task] = []
ROOT_TASK_KEY: str = "__root__"


def add_tasks(*args: Callable[..., Any] | Task, **kwargs: Callable[..., Any]) -> None:
    """Register the given callable(s) with myke.

    Arguments:
        *args: ...
        **kwargs: ...

    Raises:
        TaskAlreadyRegisteredError: ...

    Examples:
        >>> import myke
        ...
        >>> def say_hello(name):
        ...    print(f'Hello {name}.')
        ...
        >>> def say_goodbye(name):
        ...    print(f'Goodbye {name}.')
        ...
        >>> myke.add_tasks(say_hello, say_goodbye)
    """
    TASKS.extend(
        [
            x
            if isinstance(x, Task)
            else Task(name=convert_to_command_string(x.__name__), function=x)
            for x in args
        ],
    )
    TASKS.extend(
        [
            Task(
                name=(k if k == ROOT_TASK_KEY else convert_to_command_string(k)),
                function=v,
            )
            for k, v in kwargs.items()
        ],
    )


def import_mykefile(path: str) -> None:
    """Import tasks from another Mykefile.

    Args:
        path: path to the Mykefile

    Raises:
        NoTasksFoundError:

    Examples:
        >>> import myke
        ...
        >>> myke.import_mykefile('/path/to/tasks.py')  # doctest: +SKIP
    """
    n_tasks_before: int = len(TASKS)

    loader = _MykeSourceFileLoader(os.path.relpath(path), path)
    mod: ModuleType = ModuleType(loader.name)
    loader.exec_module(mod)

    if len(TASKS) <= n_tasks_before:
        raise NoTasksFoundError(path)


def import_module(name: str) -> None:
    """Import tasks from the given Python module.

    Args:
        name: name of the module.

    Raises:
        NoTasksFoundError:

    Examples:
        >>> import myke
        ...
        >>> myke.import_module('python_pkg.python_module')  # doctest: +SKIP
    """
    n_tasks_before: int = len(TASKS)

    __import__(name)

    if len(TASKS) <= n_tasks_before:
        raise NoTasksFoundError(name)


def task(
    func: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    parents: str | tuple[str | yapx.Command, ...] | None = None,
    root: bool = False,
) -> Callable[..., Any] | Callable[..., Callable[..., Any]]:
    """Function decorator to register functions with myke.

    Args:
        func: ...
        name: name of the command.
        parents: optional parent(s) for the command.
        root: if True, import this as the root command.

    Returns:
        ...

    Examples:
        >>> from myke import task
        ...
        >>> @task  # doctest: +SKIP
        ... def say_hello(name):
        ...    print(f'Hello {name}.')
        ...
        >>> @task  # doctest: +SKIP
        ... def say_goodbye(name):
        ...    print(f'Goodbye {name}.')
        ...
    """

    if not func:
        return partial(task, name=name, parents=parents, root=root)

    if root:
        name = ROOT_TASK_KEY
    elif not name:
        name = convert_to_command_string(func.__name__)

    if not parents:
        parents = ()
    elif isinstance(parents, (str, yapx.Command)):
        parents = (parents,)
    elif not isinstance(parents, tuple):
        parents = tuple(parents)

    new_task: Task = Task(name=name, function=func, parents=parents)

    add_tasks(new_task)

    return func


def shell_task(
    func: Callable[..., str | Sequence[str]] | None = None,
    *,
    name: str | None = None,
    parents: str | tuple[str] | None = None,
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
    """Function decorator to register shell commands with myke.

    myke expects the function to return a string of one or more shell-commands,
    and will invoke the commands using `myke.run(..., shell=True)`.

    Args:
        func: ...
        name: name of the command.
        parents: optional parents for the command.
        root: if True, import this as the root command.
        capture_output: ...
        echo: ...
        check: ...
        cwd: ...
        env: ...
        env_update: ...
        timeout: ...
        executable: ...

    Returns:
        ...

    Examples:
        >>> from myke import shell_task
        ...
        >>> @shell_task  # doctest: +SKIP
        ... def say_hello(name):
        ...    return f"echo 'Hello {name}.'"
        ...
        >>> @shell_task  # doctest: +SKIP
        ... def say_goodbye(name):
        ...    return f"echo 'Goodbye {name}.'"
        ...
    """
    if not func:
        return partial(
            shell_task,
            name=name,
            parents=parents,
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
                "Expected a string to be returned for the `shell_task`",
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

    return task(_inner_func, name=name, parents=parents, root=root)
