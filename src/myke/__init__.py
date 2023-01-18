from functools import lru_cache as cache

from yapx import arg

from . import exceptions, utils
from .__version__ import __version__
from .globals import TASKS
from .io.echo import echo
from .io.read import read
from .io.write import write
from .main import main
from .sh import require, run, sh, sh_stdout, sh_stdout_lines
from .tasks import (
    add_tasks,
    import_module,
    install_module,
    task,
    task_sh,
    task_sh_stdout,
    task_sh_stdout_lines,
)

__all__ = [
    "__version__",
    "TASKS",
    "task",
    "task_sh",
    "task_sh_stdout",
    "task_sh_stdout_lines",
    "add_tasks",
    "import_module",
    "install_module",
    "run",
    "sh",
    "sh_stdout",
    "sh_stdout_lines",
    "require",
    "arg",
    "main",
    "read",
    "write",
    "utils",
    "exceptions",
    "cache",
    "echo",
]
