import os
from typing import List, Pattern

import mockish
import pytest
from _pytest.capture import CaptureFixture, CaptureResult

import myke
from myke.main import main
from myke.main import sys as target_sys


def test_main_version(capsys: CaptureFixture, version_pattern: Pattern):
    # 1. ARRANGE
    args: List[str] = ["--myke-version"]

    # 2. ACT
    with mockish.patch.object(target_sys, "argv", ["", *args]), pytest.raises(
        SystemExit,
    ) as e:
        main()

    # 3. ASSERT
    assert e.value.code == 0

    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert version_pattern.search(captured.out.split()[-1]), "invalid version"


def test_main_help(capsys: CaptureFixture):
    # 1. ARRANGE
    args: List[str] = ["--myke-help"]

    # 2. ACT
    with mockish.patch.object(target_sys, "argv", ["", *args]), pytest.raises(
        SystemExit,
    ) as e:
        main()

    # 3. ASSERT
    assert e.value.code == 0

    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out


def test_main_explain(capsys: CaptureFixture, resources_dir: str):
    # 1. ARRANGE
    args: List[str] = ["--myke-explain", "hello"]

    myke.TASKS.clear()
    mykefile: str = os.path.join(resources_dir, "Mykefile")

    expected: str = '''
@task\ndef hello(name="world"):\n    """Say hello."""\n    print("hello " + name)
'''

    # 2. ACT
    myke.import_mykefile(mykefile)

    with mockish.patch.object(target_sys, "argv", ["", *args]), pytest.raises(
        SystemExit,
    ) as e:
        main(mykefile)

    # 3. ASSERT
    assert e.value.code == 0

    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out

    assert expected.strip() == captured.out.strip()
