import collections.abc
import os
from functools import partial, wraps
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from .exceptions import MykeNotFoundError, NoTasksFoundError, TaskAlreadyRegisteredError
from .globals import MYKE_VAR_NAME, ROOT_TASK_KEY, TASKS
from .io.read import read
from .io.write import write
from .sh import sh
from .utils import (
    _MykeSourceFileLoader,
    convert_to_command_string,
    make_executable,
    split_and_trim_text,
)


def add_tasks(*args: Callable[..., Any], **kwargs: Callable[..., Any]) -> None:

    kwargs.update({x.__name__: x for x in args})

    kwargs = {
        (ROOT_TASK_KEY if k == ROOT_TASK_KEY else convert_to_command_string(k)): v
        for k, v in kwargs.items()
    }

    for k, v in kwargs.items():
        v_existing: Optional[Callable[..., Any]] = TASKS.get(k, None)
        if v_existing:
            raise TaskAlreadyRegisteredError(
                f"Failed to import module '{v.__module__}': "
                f"Command '{k}' already defined from module '{v_existing.__module__}'"
            )
        TASKS[k] = v


def import_module(*mykefiles: str, overwrite: Optional[bool] = None) -> None:
    n_tasks_before: int = len(TASKS)
    for m in mykefiles:
        if m.startswith("https://"):
            m = install_module(m, overwrite=overwrite)

        loader = _MykeSourceFileLoader(os.path.relpath(m), m)
        mod: ModuleType = ModuleType(loader.name)
        loader.exec_module(mod)

        if not hasattr(mod, MYKE_VAR_NAME):
            raise MykeNotFoundError(m)

        n_tasks_after: int = len(TASKS)
        if n_tasks_after <= n_tasks_before:
            raise NoTasksFoundError(m)
        n_tasks_before = n_tasks_after


def install_module(
    url: str,
    path: Optional[str] = None,
    fail_if_exists: Optional[bool] = None,
    overwrite: Optional[bool] = None,
) -> str:
    if overwrite is None:
        overwrite = bool(os.getenv("MYKE_UPDATE_MODULES"))

    if not url.startswith("https://"):
        raise ValueError("Download URLs must start with 'https://'")

    if path is None:
        path = "tasks"

        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(path, os.path.basename(url))

    if not overwrite and not fail_if_exists and os.path.exists(path):
        return path

    resp_text: str = read.url(url)

    import_myke: str = f"import {MYKE_VAR_NAME}"
    if import_myke not in resp_text:
        raise MykeNotFoundError(f'"{import_myke}" not found response text of {url}')

    write(resp_text, path=path, overwrite=overwrite)

    make_executable(path)

    return path


def task(
    func: Optional[Callable[..., Any]] = None,
    *,
    name: Optional[str] = None,
    root: Optional[bool] = False,
) -> Union[Callable[..., Any], Callable[..., Callable[..., Any]]]:

    if not func:
        return partial(task, name=name, root=root)

    if root:
        name = ROOT_TASK_KEY

    if name:
        add_tasks(**{name: func})
    else:
        add_tasks(func)

    return func


def task_sh(
    func: Optional[Callable[..., Union[str, Sequence[str]]]] = None,
    *,
    name: Optional[str] = None,
    root: Optional[bool] = False,
    capture_output: Optional[bool] = False,
    echo: Optional[bool] = True,
    check: Optional[bool] = True,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    env_update: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    executable: Optional[str] = None,
) -> Union[
    Callable[..., Tuple[Optional[str], Optional[str], int]],
    Callable[..., Callable[..., Tuple[Optional[str], Optional[str], int]]],
]:
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
    def _inner_func(
        *args: Any, **kwargs: Any
    ) -> Tuple[Optional[str], Optional[str], int]:
        assert func

        func_script: Union[str, Sequence[str]] = func(*args, **kwargs)

        if not isinstance(func_script, str) and not isinstance(
            func_script, collections.abc.Sequence
        ):
            raise TypeError(
                "Expected a string or list of strings to be returned for `sh` function"
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


def _task_sh_stdout_lines(
    func: Optional[Callable[..., Union[str, Sequence[str]]]] = None,
    *,
    name: Optional[str] = None,
    root: Optional[bool] = False,
    echo: Optional[bool] = False,
    check: Optional[bool] = True,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    env_update: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    executable: Optional[str] = None,
    join_lines: Optional[bool] = False,
) -> Union[
    Callable[..., Union[str, List[str]]],
    Callable[..., Callable[..., Union[str, List[str]]]],
]:
    if not func:
        return partial(
            task_sh_stdout_lines,
            name=name,
            root=root,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

    @wraps(func)
    def _inner_func(*args: Any, **kwargs: Any) -> Union[str, List[str]]:
        assert func
        stdout, *_ = sh(
            func(*args, **kwargs),
            capture_output=True,
            echo=echo,
            check=check,
            cwd=cwd,
            env=env,
            env_update=env_update,
            timeout=timeout,
            executable=executable,
        )

        stdout_split: List[str] = split_and_trim_text(stdout)

        return os.linesep.join(stdout_split) if join_lines else stdout_split

    if not name:
        name = func.__name__

    return task(_inner_func, name=name, root=root)


@wraps(_task_sh_stdout_lines)
def task_sh_stdout_lines(
    *args: Any, **kwargs: Any
) -> Union[Callable[..., List[str]], Callable[..., Callable[..., List[str]]]]:
    return _task_sh_stdout_lines(*args, **kwargs)  # type: ignore


@wraps(_task_sh_stdout_lines)
def task_sh_stdout(
    *args: Any, **kwargs: Any
) -> Union[Callable[..., str], Callable[..., Callable[..., str]]]:
    kwargs["join_lines"] = True
    return _task_sh_stdout_lines(*args, **kwargs)  # type: ignore
