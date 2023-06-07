import subprocess
from typing import List

import pytest
from _pytest.capture import CaptureFixture, CaptureResult

import myke


def test_run(capfd: CaptureFixture):
    expected: str = "hello world"
    p: subprocess.CompletedProcess = myke.run(["python", "-c", f"print('{expected}')"])

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert captured.out.rstrip() == expected

    assert p.returncode == 0
    assert not p.stderr
    assert not p.stdout


def test_run_shell(capfd: CaptureFixture):
    expected: str = "hello world"
    p: subprocess.CompletedProcess = myke.run(f'echo "{expected}"')

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert captured.out.rstrip() == expected

    assert p.returncode == 0
    assert not p.stderr
    assert not p.stdout


def test_run_no_echo(capfd: CaptureFixture):
    expected: str = "hello world"
    p: subprocess.CompletedProcess = myke.run(f'echo "{expected}"', echo=False)

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert p.returncode == 0
    assert not p.stderr
    assert not p.stdout


def test_run_capture_no_echo(capfd: CaptureFixture):
    expected: str = "hello world"
    p: subprocess.CompletedProcess = myke.run(
        f'echo "{expected}"',
        capture_output=True,
        text=True,
        echo=False,
    )

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert p.returncode == 0
    assert not p.stderr
    assert p.stdout.rstrip() == expected


def test_run_check():
    with pytest.raises(subprocess.CalledProcessError):
        myke.run("exit 1")


def test_run_no_check():
    expected: int = 1
    p: subprocess.CompletedProcess = myke.run(f"exit {expected}", check=False)
    assert p.returncode == expected


def test_sh():
    expected: str = "hello"
    cmd: str = f"echo -n {expected}"
    assert myke.sh(cmd, capture_output=True).stdout.decode("utf-8") == expected


def test_sh_stdout_lines():
    expected: List[str] = ["hello", "world"]
    cmd: str = "echo '" + "\\n".join(expected) + "'"
    stdout: List[str] = myke.sh_stdout_lines(cmd)

    assert stdout == expected


def test_sh_stdout():
    expected: List[str] = ["hello", "world"]
    cmd: str = "echo '" + "\\n".join(expected) + "'"
    stdout: str = myke.sh_stdout(cmd)

    assert stdout == "\n".join(expected)


def test_require(capfd: CaptureFixture):
    p: subprocess.CompletedProcess = myke.require(
        pip_args=[
            "--extra-index-url",
            "https://codeberg.org/api/packages/Fresh2dev/pypi/simple",
            "--quiet",
            "--dry-run",
        ],
        mykefiles="0.0.1a3.dev44",
    )

    captured: CaptureResult = capfd.readouterr()
    assert not captured.err
    assert not captured.out

    assert p.returncode == 0
    assert not p.stderr
