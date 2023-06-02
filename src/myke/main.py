import os
import sys
from contextlib import suppress
from dataclasses import dataclass
from fnmatch import fnmatch
from inspect import getsource
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import yapx

from .__version__ import __version__
from .exceptions import NoTasksFoundError
from .globals import DEFAULT_MYKEFILE, MYKE_VAR_NAME, ROOT_TASK_KEY, TASKS
from .io.echo import echo
from .io.write import write
from .tasks import import_module, import_mykefile
from .types import Annotated
from .utils import get_repo_root

__all__ = ["__version__", "main", "sys"]


def main(_file: Optional[Union[str, Path]] = None) -> None:
    @dataclass
    class MykeArgs(yapx.types.Dataclass):
        file: Annotated[
            Optional[Path],
            yapx.arg(
                default=_file if _file else None,
                flags=["--myke-file"],
                env="MYKE_FILE",
                group="myke args",
            ),
        ]
        module: Annotated[
            Optional[str],
            yapx.arg(
                default=None,
                flags=["--myke-module"],
                env="MYKE_MODULE",
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
        create: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--myke-create"],
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
        show_tui: Annotated[
            Optional[bool],
            yapx.arg(
                default=None,
                group="myke args",
                exclusive=True,
                flags=["--tui", "--myke-tui"],
            ),
        ]

    prog: str = str(_file) if _file else MYKE_VAR_NAME

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

    if not myke_args.file and Path(DEFAULT_MYKEFILE).exists():
        myke_args.file = Path(DEFAULT_MYKEFILE)

    if myke_args.create:
        write.mykefile(str(myke_args.file))
        echo(f"Created: {myke_args.file}")
        parser.exit()

    with suppress(FileNotFoundError):
        repo_root: Optional[Path] = get_repo_root()
        if repo_root:
            os.chdir(repo_root)

    if _file:
        if not isinstance(_file, Path):
            _file = Path(_file)
        if not _file.exists():
            raise FileNotFoundError(_file)
        if not TASKS:
            raise NoTasksFoundError(_file)
        _file = _file.absolute()

    try:
        if myke_args.file and (not _file or not myke_args.file.samefile(_file)):
            import_mykefile(str(myke_args.file.absolute()))
    except FileNotFoundError:
        parser.print_help()
        echo(
            (
                f"{os.linesep}"
                f"'{myke_args.file}' not found. Create it using:"
                f"{os.linesep}"
                f"> {prog} --myke-create --myke-file '{myke_args.file}'"
                f"{os.linesep}"
            ),
        )
        parser.exit()

    if myke_args.module:
        import_module(myke_args.module)

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

    if not task_args and not myke_args.help and not myke_args.show_tui:
        myke_args.show_tui = yapx.utils.is_tui_available()
        myke_args.help = not myke_args.show_tui

    if myke_args.help:
        parser.print_help()
        echo.tasks(prog=prog)
        parser.exit()

    if task_args:
        for k in list(TASKS):
            if not fnmatch(k, task_args[0]):
                del TASKS[k]
        if not TASKS and not myke_args.task_help_full:
            echo.tasks(prog=prog)
            parser.exit()

    if myke_args.task_help:
        task_args.append("--help")

    tui_flags: Optional[List[str]] = ["--tui"] if myke_args.show_tui else None
    if tui_flags:
        task_args.extend(tui_flags)

    yapx.run(
        root_task,
        _args=task_args,
        _prog=prog,
        _print_help=bool(myke_args.task_help_full),
        _tui_flags=tui_flags,
        **TASKS,
    )
