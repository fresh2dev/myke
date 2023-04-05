import os
import subprocess
from typing import List, Union
from unittest import mock
from uuid import uuid4

import pytest

from myke import sh_stdout


def _common(
    capsys,
    resources_dir: str,
    cli_args: List[str],
    expected_txt: Union[str, List[str]],
):
    # 1. ARRANGE
    import myke
    from myke.main import sys as target_sys

    myke.TASKS.clear()

    mykefile: str = os.path.join(resources_dir, "Mykefile")

    # 2. ACT
    myke.import_module(mykefile)

    with mock.patch.object(target_sys, "argv", [""] + cli_args):
        myke.main(mykefile)

    # 3. ASSERT
    captured = capsys.readouterr()

    if expected_txt:
        if isinstance(expected_txt, str):
            assert expected_txt in captured.out
        else:
            for exp in expected_txt:
                assert exp in captured.out

    return captured


def test_Mykefile_setup(capsys, resources_dir: str):
    expected_txt = "charging lazer beamz"
    cli_args: List[str] = ["hello", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_named(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello-named", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_named2(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello-named2", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_named3(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello-named3", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_positional(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello-positional", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_positional_default(capsys, resources_dir: str):
    expected_txt = "hello world"
    cli_args: List[str] = ["hello-positional"]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_positional_bool_true(capsys, resources_dir: str):
    expected_txt = "hello world".upper()
    cli_args: List[str] = ["hello-positional-bool", "y"]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_positional_bool_false(capsys, resources_dir: str):
    expected_txt = "hello world"
    cli_args: List[str] = ["hello-positional-bool", "n"]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_othermyke(capsys, resources_dir: str):
    expected_txt = str(uuid4())
    cli_args: List[str] = ["hello-othermyke", "--name", expected_txt]
    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=expected_txt)


def test_Mykefile_hello_check(capsys, resources_dir: str):
    cli_args: List[str] = ["hello-check"]

    with pytest.raises(subprocess.CalledProcessError):
        _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt="...")


def test_Mykefile_hello_timeout(capsys, resources_dir: str):
    cli_args: List[str] = ["hello-timeout"]

    with pytest.raises(subprocess.TimeoutExpired):
        _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt="...")


def test_Mykefile_assert_types(capsys, resources_dir: str):
    cli_args: List[str] = [
        "assert-types",
        "--xstr",
        "hello",
        "--xint",
        "5",
        "--xfloat",
        "3.14",
        "--xbool",
        "--xliststr",
        "list[this that]",
        "list[another]",
        "--xsetint",
        "list[1 1]",
        "list[1 2]",
        "list[  3  ]",
        "--xtuplefloat",
        "list[3.14]",
        "list[6.28 9.42]",
    ]

    _ = _common(capsys, resources_dir, cli_args=cli_args, expected_txt=None)


def test_Mykefile_executable(capsys, resources_dir: str):
    # 1. ARRANGE
    mykefile: str = os.path.join(resources_dir, "Mykefile")

    expected_txt: str = str(uuid4())

    # 2. ACT
    output: str = sh_stdout(
        f"""
    PYTHONPATH=./src python -m myke --myke-file {mykefile} hello --name {expected_txt}
""",
        echo=True,
    )

    # 3. ASSERT
    assert output
    assert expected_txt in output

    captured = capsys.readouterr()
    assert captured.out
    assert not captured.err
    assert expected_txt in captured.out
