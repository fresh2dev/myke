# myke

> The dynamic Python CLI for task execution.

| Links         |                                              |
|---------------|----------------------------------------------|
| Code Repo     | https://www.github.com/fresh2dev/myke        |
| Mirror Repo   | https://www.f2dv.com/code/r/myke             |
| Documentation | https://www.f2dv.com/code/r/myke/i           |
| Changelog     | https://www.f2dv.com/code/r/myke/i/changelog |
| License       | https://www.f2dv.com/code/r/myke/i/license   |
| Funding       | https://www.f2dv.com/funding                 |

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/fresh2dev/myke?color=blue&style=for-the-badge)](https://www.github.com/fresh2dev/myke/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/fresh2dev/myke?color=blue&style=for-the-badge)](https://www.github.com/fresh2dev/myke/releases)
[![License](https://img.shields.io/github/license/fresh2dev/myke?color=blue&style=for-the-badge)](https://www.f2dv.com/code/r/myke/i/license)
[![GitHub issues](https://img.shields.io/github/issues-raw/fresh2dev/myke?color=blue&style=for-the-badge)](https://www.github.com/fresh2dev/myke/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/fresh2dev/myke?color=blue&style=for-the-badge)](https://www.github.com/fresh2dev/myke/pulls)
[![GitHub Repo stars](https://img.shields.io/github/stars/fresh2dev/myke?color=blue&style=for-the-badge)](https://star-history.com/#fresh2dev/myke&Date)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/myke?color=blue&style=for-the-badge)](https://pypi.org/project/myke)
[![Docker Pulls](https://img.shields.io/docker/pulls/fresh2dev/myke?color=blue&style=for-the-badge)](https://hub.docker.com/r/fresh2dev/myke)
[![Docs Website](https://img.shields.io/website?down_message=unavailable&label=docs&style=for-the-badge&up_color=blue&up_message=available&url=https://www.f2dv.com/code/r/myke/i)](https://www.f2dv.com/code/r/myke/i)
[![Coverage Website](https://img.shields.io/website?down_message=unavailable&label=coverage&style=for-the-badge&up_color=blue&up_message=available&url=https://www.f2dv.com/code/r/myke/i/tests/coverage)](https://www.f2dv.com/code/r/myke/i/tests/coverage)
[![Funding](https://img.shields.io/badge/funding-%24%24%24-blue?style=for-the-badge)](https://www.f2dv.com/funding)

---

Meet `myke`, the dynamic Python CLI for task exection.

I built `myke` to replace my personal need for `make` and Makefiles. myke has probably 1% of the functionality of make, and that's a good thing.

> Note: `myke` is in *beta* status. Please report ideas and issues [here](https://github.com/fresh2dev/myke/issues).

## Install

myke is a CLI application, so I recommend installing it using [pipx](https://github.com/pypa/pipx).

```sh
pipx install 'myke[extras]'
```

What's in `myke[extras]`?

- `myke[io]` --> Libraries to read/write various file formats (yaml, toml, etc.)
- `myke[pydantic]` --> Includes the [Pydantic](https://github.com/pydantic/pydantic) library to support additional types.
- `myke[tui]` --> Includes the [Trogon](https://github.com/Textualize/trogon) library to present a TUI for myke.

## Use

Paste the following into a file named `Mykefile`:

```python title="Mykefile"
from myke import task

@task
def say_hello(name):
    print(f"Hello {name}.")

@task
def say_goodbye(name):
    print(f"Goodbye {name}.")
```

Invoke a task:

```sh
myke say-hello --name world
```

View available tasks:

```sh
myke
```

## Read More

myke is an instantiation of the `yapx` project, the CLI builder for Python. The information contained in the [yapx docs](https://www.f2dv.com/code/r/yapx/i/) also applies to myke.

Read more about myke @ https://www.f2dv.com/code/r/myke/i

Read more about yapx @ https://www.f2dv.com/code/r/yapx/i

See all of my projects @ https://www.f2dv.com/code/r

*Brought to you by...*

<a href="https://www.fresh2.dev"><img src="https://img.fresh2.dev/fresh2dev.svg" style="filter: invert(50%);"></img></a>
