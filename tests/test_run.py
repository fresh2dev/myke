import subprocess
from typing import List

import pytest
from _pytest.capture import CaptureFixture, CaptureResult

import myke


def test_run(capfd: CaptureFixture):
    expected: str = "hello world"
    stdout, stderr, returncode = myke.run(["python", "-c", f"print('{expected}')"])

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert captured.out.rstrip() == expected

    assert returncode == 0
    assert not stderr
    assert not stdout


def test_run_shell(capfd: CaptureFixture):
    expected: str = "hello world"
    stdout, stderr, returncode = myke.run(f'echo "{expected}"')

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert captured.out.rstrip() == expected

    assert returncode == 0
    assert not stderr
    assert not stdout


def test_run_no_echo(capfd: CaptureFixture):
    expected: str = "hello world"
    stdout, stderr, returncode = myke.run(f'echo "{expected}"', echo=False)

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert returncode == 0
    assert not stderr
    assert not stdout


def test_run_capture_no_echo(capfd: CaptureFixture):
    expected: str = "hello world"
    stdout, stderr, returncode = myke.run(
        f'echo "{expected}"', capture_output=True, echo=False
    )

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert returncode == 0
    assert not stderr
    assert stdout.rstrip() == expected


def test_run_check():
    with pytest.raises(subprocess.CalledProcessError):
        myke.run("exit 1")


def test_run_no_check():
    expected: int = 1
    _, _, returncode = myke.run(f"exit {expected}", check=False)
    assert returncode == expected


def test_sh():
    cmd: str = "echo hello"
    assert myke.run(cmd, shell=True) == myke.sh(cmd)


def test_sh_stdout_lines():
    expected: List[str] = ["hello", "world"]
    cmd: str = "echo '" + "\\n".join(expected) + "'"
    stdout = myke.sh_stdout_lines(cmd)

    assert stdout == expected


def test_sh_stdout():
    expected: List[str] = ["hello", "world"]
    cmd: str = "echo '" + "\\n".join(expected) + "'"
    stdout = myke.sh_stdout(cmd)

    assert stdout == "\n".join(expected)


def test_require(capfd: CaptureFixture):
    stdout, stderr, returncode = myke.require(
        "mykefiles==0.0.1a3.dev20",
        pip_args=[
            "--extra-index-url",
            "https://codeberg.org/api/packages/Fresh2dev/pypi/simple",
        ],
    )

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert returncode == 0
    assert not stderr
    assert stdout
