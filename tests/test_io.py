import os
from pathlib import Path
from typing import Any, Dict, List

import pytest

import myke


def test_read_text(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.txt")

    # 2. ACT
    content: str = myke.read(file)

    # 3. ASSERT
    assert content
    assert isinstance(content, str)
    assert content.startswith("hello")
    assert content.endswith("world")


def test_read_lines(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.txt")

    # 2. ACT
    content: List[str] = myke.read.lines(file)

    # 3. ASSERT
    assert content
    assert content == ["hello", "world"]


def test_read_json(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.json")

    # 2. ACT
    content: Dict[str, Any] = myke.read.json(file)

    # 3. ASSERT
    assert content
    assert content == {"hello": "world"}


def test_read_yaml(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.yaml")

    # 2. ACT
    content: Dict[str, Any] = myke.read.yaml(file)

    # 3. ASSERT
    assert content
    assert content == {"hello": "world"}


def test_read_yaml_all(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test-all.yaml")

    # 2. ACT
    content: Dict[str, Any] = myke.read.yaml_all(file)

    # 3. ASSERT
    assert content
    assert content == [{"hello": "world"}, {"goodbye": "cruel world"}]


def test_read_toml(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.toml")

    # 2. ACT
    content: Dict[str, Any] = myke.read.toml(file)

    # 3. ASSERT
    assert content
    assert content == {
        "arrival": {"hello": "world"},
        "departure": {"goodbye": "cruel world"},
    }


def test_read_cfg(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.cfg")

    # 2. ACT
    content: Dict[str, Any] = myke.read.cfg(file)

    # 3. ASSERT
    assert content
    assert content == {
        "arrival": {"hello": "world"},
        "departure": {"goodbye": "cruel world"},
    }
    assert myke.read.ini(file) == content


def test_read_dotfile(resources_dir: str):
    # 1. ARRANGE
    file: str = os.path.join(resources_dir, "files", "test.env")

    # 2. ACT
    content: Dict[str, Any] = myke.read.dotfile(file)

    # 3. ASSERT
    assert content
    assert content == {"hello": "world", "goodbye": "cruel world"}
    assert myke.read.envfile(file) == content


def test_read_url():
    url: str = (
        "https://codeberg.org/fresh2dev/copier-f2dv-project/raw/branch/main/LICENSE"
    )

    resp: str = myke.read.url(url)

    assert resp
    assert isinstance(resp, str)


def test_write_text(tmp_path: Path):
    expected: str = "hello world"

    path = str(tmp_path / "dummy.txt")
    myke.write(expected, path)

    assert os.path.exists(path)
    assert myke.read(path) == expected

    myke.write(expected, path, append=True)
    assert myke.read(path) == expected * 2

    with pytest.raises(FileExistsError):
        myke.write(content=expected, path=path)


def test_write_lines(tmp_path: Path):
    expected: List[str] = ["hello", "world"]

    path = tmp_path / "dummy.txt"
    myke.write.lines(path=path, content=expected)

    assert path.exists()
    assert myke.read.lines(path) == expected

    with pytest.raises(TypeError):
        myke.write.lines(path=path, content=str(expected))


def test_echo_text(capsys):
    test_input: str = "hello world"
    expected: str = test_input + os.linesep

    myke.echo(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_echo_lines(capsys):
    test_input: List[str] = ["hello", None, "world", None]
    expected: str = os.linesep.join([str(x) for x in test_input]) + os.linesep

    myke.echo.lines(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_echo_json(capsys):
    test_input: List[str] = ["hello", "world"]
    expected: str = '["hello", "world"]' + os.linesep

    myke.echo.json(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_echo_table(capsys):
    test_input: List[str] = [{"hello": "world"}, {"hello": "world2"}]
    expected: str = "hello\n-------\nworld\nworld2\n"

    myke.echo.table(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_echo_pretty(capsys):
    test_input: str = "hello world"
    expected: str = f"'{test_input}'" + os.linesep

    myke.echo.pretty(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_echo_tasks(capsys):
    myke.TASKS.clear()
    expected: str = "No tasks found."

    myke.echo.tasks()

    captured = capsys.readouterr()
    assert expected in captured.out
