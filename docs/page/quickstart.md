# Quick Start

There are some parameters specific to `myke`, each of them prefixed with `--myke-...` in order to not conflict with parameters of your own root-command.

For example, to print help and print all registered tasks:

```sh
$ myke --myke-help

usage: myke [--myke-file FILE] [--myke-module MODULE] [--myke-help]
            [--myke-explain] [--myke-create] [--myke-version]

myke args:
  --myke-file FILE      > Type: Path, Default: None, Env: ['MYKE_FILE']
  --myke-module MODULE  > Type: str, Default: 'mykefiles.python', Env:
                        ['MYKE_MODULE']
  --myke-help           > Type: bool, Default: None, M.X.
  --myke-explain        > Type: bool, Default: None, M.X.
  --myke-create         > Type: bool, Default: None, M.X.
  --myke-version        > Type: bool, Default: None, M.X.

===============  ================
Task             Source
===============  ================
do-work          Mykefile
more-work        Mykefile
...
===============  ================

To view task parameters, see:
> myke <task-name> --help
```

## Create a Mykefile

Create your first Mykefile with:

```sh
$ myke --myke-create

Created: Mykefile
```

Specify an alternative Mykefile with:

```sh
$ myke --myke-file /path/to/tasks.py
```

To import a Python module containing myke tasks:

```sh
$ myke --myke-module my_package.my_module
```

To print a task definition:

```sh
$ myke --myke-explain <task-mame>
```

To list tasks that match glob pattern:

```sh
$ myke 'test-*'
```

To invoke a task:

```sh
$ myke <root-task-args> <task-name> <task-args>
```

e.g.,

```sh
$ myke --log-level debug publish-dist --build
```
