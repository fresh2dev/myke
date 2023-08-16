# Quick Start

There are some parameters specific to `myke`, each of them prefixed with `--myke-...` in order to not conflict with parameters of your own root-command.

```sh
________________________________________________________________________________

$ myke --myke-help
________________________________________________________________________________

Helpful Parameters:
  --myke-help           Show this help message.
  --myke-help-all       Show help for all commands.
  --myke-version        Show the program version number.

Myke Parameters:
  --myke-file <value>   > Type: Path], Env: ['MYKE_FILE']
  --myke-module <value>
                        > Type: List, Env: ['MYKE_MODULE']
  --myke-tasks, --no-myke-tasks
                        > Type: bool, M.X.
  --myke-explain, --no-myke-explain
                        > Type: bool, M.X.
  --myke-create, --no-myke-create
                        > Type: bool, M.X.
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
$ myke --myke-explain <task-name>
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
