import os
import sys
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from inspect import getsource
from pathlib import Path
from subprocess import CalledProcessError
from typing import Dict, List, Optional, Tuple, Union

import yapx

from .__version__ import __version__
from .exceptions import NoTasksFoundError, TaskAlreadyRegisteredError
from .globals import DEFAULT_MYKEFILE, MYKE_VAR_NAME
from .io.echo import echo
from .io.write import write
from .tasks import ROOT_TASK_KEY, TASKS, Task, import_module, import_mykefile
from .types import Annotated
from .utils import get_repo_root

__all__ = ["__version__", "main", "sys"]


def main(_file: Optional[Union[str, Path]] = None) -> None:
    @dataclass
    class MykeArgs(yapx.types.Dataclass):
        file: Annotated[
            Optional[List[Path]],
            yapx.arg(
                "myke-file",
                default=_file if _file else None,
                env="MYKE_FILE",
                group="myke parameters",
            ),
        ]
        module: Annotated[
            Optional[List[str]],
            yapx.arg(
                "myke-module",
                default=None,
                env="MYKE_MODULE",
                group="myke parameters",
            ),
        ]
        list_tasks: Annotated[
            Optional[bool],
            yapx.arg(
                "myke-tasks",
                default=None,
                group="myke parameters",
                exclusive=True,
            ),
        ]
        explain: Annotated[
            Optional[bool],
            yapx.arg(
                "myke-explain",
                default=None,
                group="myke parameters",
                exclusive=True,
            ),
        ]
        create: Annotated[
            Optional[bool],
            yapx.arg(
                "myke-create",
                default=None,
                group="myke parameters",
                exclusive=True,
            ),
        ]

    prog: str = str(_file) if _file else MYKE_VAR_NAME

    parser = yapx.ArgumentParser(
        prog=prog,
        prog_version=__version__,
        help_flags=["--myke-help"],
        version_flags=["--myke-version"],
        completion_flags=[],
        tui_flags=[],
    )
    parser.add_arguments(MykeArgs)

    args = sys.argv[1:]

    myke_args: MykeArgs
    task_args: List[str]
    myke_args, task_args = parser.parse_known_args_to_model(
        args,
        args_model=MykeArgs,
        skip_pydantic_validation=True,
    )
    assert isinstance(myke_args, MykeArgs)

    if _file:
        if not isinstance(_file, Path):
            _file = Path(_file)
        if not _file.exists():
            raise FileNotFoundError(_file)
        if not TASKS:
            raise NoTasksFoundError(_file)
        _file = _file.absolute()

    if myke_args.file:
        myke_args.file = [x.absolute() for x in myke_args.file]
    elif Path(DEFAULT_MYKEFILE).exists():
        myke_args.file = [Path(DEFAULT_MYKEFILE).absolute()]

    with suppress(FileNotFoundError):
        repo_root: Optional[Path] = get_repo_root()
        if repo_root:
            os.chdir(repo_root)

    if not myke_args.file:
        if Path(DEFAULT_MYKEFILE).exists():
            myke_args.file = [Path(DEFAULT_MYKEFILE).absolute()]
        else:
            myke_args.file = []

    if myke_args.create:
        out_file: Path = myke_args.file[0] if myke_args.file else Path(DEFAULT_MYKEFILE)
        write.mykefile(str(out_file))
        echo(f"Created: {out_file}")
        parser.exit()

    try:
        try:
            for f in myke_args.file:
                if f and (not _file or not f.samefile(_file)):
                    import_mykefile(str(f))
                    # TODO: os.environ["MYKE_FILE"] = str(myke_args.file)
        except FileNotFoundError as e:
            parser.print_help()
            echo(
                (
                    f"{os.linesep}"
                    f"'{e.filename}' not found. Create it using:"
                    f"{os.linesep}"
                    f"$ {prog} --myke-create --myke-file '{e.filename}'"
                    f"{os.linesep}"
                ),
            )
            parser.exit()

        if myke_args.module:
            for m in myke_args.module:
                import_module(m)
                # TODO: os.environ["MYKE_MODULE"] = x
    except TaskAlreadyRegisteredError as e:
        parser.error(str(e))

    root_task: Optional[Task] = None
    root_tasks: List[Task] = [x for x in TASKS if x.name == ROOT_TASK_KEY]
    if root_tasks:
        root_task = root_tasks[0]

    if myke_args.explain:
        explain_this: Optional[Task] = None

        if not task_args or task_args[0].startswith("-"):
            explain_this = root_task
            if explain_this is None:
                echo("There is no root task. Provide a task name to explain.")
        else:
            explain_this_list: List[Task] = [x for x in TASKS if x.name == task_args[0]]
            if not explain_this_list:
                echo(f"Given task name not found: {task_args[0]}")
            else:
                explain_this = explain_this_list[0]

        if explain_this:
            echo(getsource(explain_this.function))

        parser.exit()

    if myke_args.list_tasks:
        echo.tasks(prog=prog)
        parser.exit()

    task_parents: Dict[
        Optional[Tuple[Union[str, yapx.Command], ...]],
        List[yapx.Command],
    ] = defaultdict(
        list,
    )
    for x in TASKS:
        task_parents[x.parents].append(yapx.cmd(x.function, x.name))

    def defaultdict_recursive():
        return defaultdict(defaultdict_recursive)

    subcommands: yapx.CommandMap = defaultdict_recursive()

    for parents_list, cmds_list in task_parents.items():
        this_dict = subcommands

        leaf_parent: Optional[Union[str, yapx.Command]] = None
        if parents_list:
            parent_cmds: List[yapx.Command] = [
                yapx.cmd(None, name=x) if isinstance(x, str) else x
                for x in parents_list
            ]

            leaf_parent = parent_cmds[-1]
            for parent in parent_cmds[:-1]:
                this_dict = this_dict[parent]

        this_dict[leaf_parent] = cmds_list

    try:
        yapx.run(
            None if root_task is None else root_task.function,
            subcommands=subcommands,
            args=task_args,
            default_args=["--tui"],
            prog=prog,
            prog_version=__version__,
        )
    except CalledProcessError as e:
        print(e)
        if e.output:
            print(f"stdout: {e.output}")
        elif e.stderr:
            print(f"stderr: {e.stderr}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        pass
