import os
import sys
from dataclasses import dataclass
from fnmatch import fnmatch
from inspect import getsource
from pathlib import Path
from typing import Any, Callable, List, Optional

import yapx

from .__version__ import __version__
from .exceptions import NoTasksFoundError
from .globals import DEFAULT_MYKEFILE, MYKE_VAR_NAME, ROOT_TASK_KEY, TASKS
from .io.echo import echo
from .io.read import read
from .io.write import write
from .tasks import import_module
from .types import Annotated
from .utils import get_repo_root

__all__ = ["__version__", "main", "sys"]


def main(_file: Optional[str] = None) -> None:
    @dataclass
    class MykeArgs(yapx.types.Dataclass):
        file: Annotated[
            str,
            yapx.arg(
                default=_file if _file else DEFAULT_MYKEFILE,
                flags=["--myke-file"],
                env="MYKE_FILE",
                group="myke args",
            ),
        ]
        file_paths: Annotated[
            List[str],
            yapx.arg(
                default=lambda: [os.path.expanduser("~"), os.getcwd()],
                flags=["--myke-file-paths"],
                env="MYKE_FILE_PATHS",
                group="myke args",
            ),
        ]
        env_file: Annotated[
            Optional[str],
            yapx.arg(
                default=None,
                flags=["--myke-env-file"],
                env="MYKE_ENV_FILE",
                group="myke args",
            ),
        ]
        update_modules: Annotated[
            bool,
            yapx.arg(
                default=False,
                flags=["--myke-update-modules"],
                env="MYKE_UPDATE_MODULES",
                group="myke args",
            ),
        ]
        task_help: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["-h", "--help"],
            ),
        ]
        task_help_full: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--help-full"],
            ),
        ]
        help: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--myke-help"],
            ),
        ]
        explain: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--myke-explain"],
            ),
        ]
        version: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--myke-version"],
            ),
        ]
        create: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--myke-create"],
            ),
        ]

    prog: str = _file if _file else MYKE_VAR_NAME

    parser = yapx.ArgumentParser(
        prog=prog,
        add_help=False,
        description="Parameters for Myke:",
    )
    parser.add_arguments(MykeArgs)

    myke_args: MykeArgs
    task_args: List[str]
    myke_args, task_args = parser.parse_known_args_to_model(
        sys.argv[1:],
        args_model=MykeArgs,
        skip_pydantic_validation=True,
    )
    assert isinstance(myke_args, MykeArgs)

    if myke_args.version:
        echo(__version__)
        parser.exit()
    elif myke_args.create:
        write.mykefile(myke_args.file)
        echo(f"Created: {myke_args.file}")
        parser.exit()

    if myke_args.env_file:
        os.environ.update(read.envfile(myke_args.env_file))

    if myke_args.update_modules:
        os.environ["MYKE_UPDATE_MODULES"] = "1"

    repo_root: Optional[Path] = get_repo_root()
    if repo_root:
        os.chdir(repo_root)

    if _file:
        if not os.path.exists(_file):
            raise FileNotFoundError(_file)
        if not TASKS:
            raise NoTasksFoundError(_file)
        _file = os.path.abspath(_file)

    mykefiles: List[str] = (
        [myke_args.file]
        if os.path.dirname(myke_args.file)
        else [
            y
            for x in myke_args.file_paths
            for y in [os.path.join(x, myke_args.file)]
            if os.path.exists(y)
        ]
    )

    for f in mykefiles:
        f = os.path.abspath(f)
        try:
            if f != _file:
                import_module(f)
            elif not TASKS:
                raise NoTasksFoundError(f)
        except FileNotFoundError:
            parser.print_help()
            echo(
                (
                    f"{os.linesep}"
                    f"'{myke_args.file}' not found. Create it using:"
                    f"{os.linesep}"
                    f"> {prog} --myke-create --myke-file '{f}'"
                    f"{os.linesep}"
                ),
            )
            parser.exit()

    root_task: Optional[Callable[..., Any]] = TASKS.pop(ROOT_TASK_KEY, None)

    if myke_args.explain:
        explain_this: Optional[Callable[..., Any]] = None

        if not task_args or task_args[0].startswith("-"):
            explain_this = root_task
            if explain_this is None:
                echo("There is no root task. Provide a task name to explain.")
        else:
            explain_this = TASKS.get(task_args[0], None)
            if explain_this is None:
                echo(f"Given task name not found: {task_args[0]}")

        if explain_this:
            echo(getsource(explain_this))

        parser.exit()

    if myke_args.help or (not task_args and not myke_args.task_help_full):
        parser.print_help()
        echo.tasks(prog=prog)
        parser.exit()

    if task_args and "*" in task_args[0]:
        for k in list(TASKS):
            if not fnmatch(k, task_args[0]):
                del TASKS[k]
        if not myke_args.task_help_full:
            echo.tasks(prog=prog)
            parser.exit()

    if myke_args.task_help:
        task_args.append("--help")

    yapx.run(
        root_task,
        _args=task_args,
        _prog=prog,
        _print_help=bool(myke_args.task_help_full),
        **TASKS,
    )
