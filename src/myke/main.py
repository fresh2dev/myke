__all__ = ["__version__", "main", "sys"]

import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import yapx

from .__version__ import __version__
from .exceptions import NoTasksFoundError
from .globals import DEFAULT_MYKEFILE, MYKE_VAR_NAME, ROOT_TASK_KEY, TASKS
from .io.echo import echo
from .io.read import read
from .io.write import write
from .tasks import import_module


def main(_file: Optional[str] = None) -> None:
    @dataclass
    class MykeArgs(yapx.types.Dataclass):
        file: str = yapx.arg(
            default=_file if _file else DEFAULT_MYKEFILE,
            flags=["--myke-file"],
            env_var="MYKE_FILE",
            group="myke args",
        )
        file_paths: List[str] = yapx.arg(
            default=lambda: [os.path.expanduser("~"), os.getcwd()],
            flags=["--myke-file-paths"],
            env_var="MYKE_FILE_PATHS",
            group="myke args",
        )
        env_file: str = yapx.arg(
            default=None,
            flags=["--myke-env-file"],
            env_var="MYKE_ENV_FILE",
            group="myke args",
        )
        update_modules: bool = yapx.arg(
            default=False,
            flags=["--myke-update-modules"],
            env_var="MYKE_UPDATE_MODULES",
            group="myke args",
        )
        no_pydantic: bool = yapx.arg(
            default=False, group="myke args", flags=["--myke-no-pydantic"]
        )
        task_help: bool = yapx.arg(
            default=False, group="myke args", exclusive=True, flags=["-h", "--help"]
        )
        task_help_all: bool = yapx.arg(
            default=False, group="myke args", exclusive=True, flags=["--help-all"]
        )
        help: bool = yapx.arg(
            default=False, group="myke args", exclusive=True, flags=["--myke-help"]
        )
        version: bool = yapx.arg(
            default=False, group="myke args", exclusive=True, flags=["--myke-version"]
        )
        create: bool = yapx.arg(
            default=False, group="myke args", exclusive=True, flags=["--myke-create"]
        )

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
        sys.argv[1:], args_model=MykeArgs, use_pydantic=False
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
                f"{os.linesep}"
                f"'{myke_args.file}' not found. Create it using:"
                f"{os.linesep}"
                f"> {prog} --myke-create --myke-file '{f}'"
                f"{os.linesep}"
            )
            parser.exit()

    root_task: Optional[Callable[..., Any]] = TASKS.pop(ROOT_TASK_KEY, None)

    if myke_args.help or (not task_args and not myke_args.task_help_all):
        parser.print_help()
        echo.tasks(prog=prog)
        parser.exit()

    if myke_args.task_help:
        task_args.append("--help")

    yapx.run(
        root_task,
        _args=task_args,
        _prog=prog,
        _print_help=myke_args.task_help_all,
        _use_pydantic=(not myke_args.no_pydantic),
        **TASKS,
    )
