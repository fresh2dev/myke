import os
from typing import List, Pattern
from unittest import mock

import pytest
from _pytest.capture import CaptureFixture, CaptureResult

import myke
from myke.main import sys as target_sys


def test_main_version(capsys: CaptureFixture, version_regex: Pattern):
    # 1. ARRANGE
    args: List[str] = ["--myke-version"]

    # 2. ACT
    with mock.patch.object(target_sys, "argv", [""] + args), pytest.raises(
        SystemExit,
    ) as pexit:
        myke.main()

    # 3. ASSERT
    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert version_regex.search(captured.out), "invalid version"
    assert pexit.value.code == 0


def test_main_help(capsys: CaptureFixture):
    # 1. ARRANGE
    args: List[str] = ["--myke-help"]

    # 2. ACT
    with mock.patch.object(target_sys, "argv", [""] + args), pytest.raises(
        SystemExit,
    ) as pexit:
        myke.main()

    # 3. ASSERT
    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert pexit.value.code == 0


def test_main_explain(capsys: CaptureFixture, resources_dir: str):
    # 1. ARRANGE
    args: List[str] = ["--myke-explain", "hello"]

    myke.TASKS.clear()
    mykefile: str = os.path.join(resources_dir, "Mykefile")

    expected: str = '''
@myke.task\ndef hello(name="world"):\n    """Say hello."""\n    print("hello " + name)
'''

    # 2. ACT
    myke.import_module(mykefile)

    with mock.patch.object(target_sys, "argv", [""] + args), pytest.raises(
        SystemExit,
    ) as pexit:
        myke.main(mykefile)

    # 3. ASSERT
    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert pexit.value.code == 0

    assert expected.strip() == captured.out.strip()
