from typing import List, Pattern
from unittest import mock

import pytest
from _pytest.capture import CaptureFixture, CaptureResult

from myke.main import main
from myke.main import sys as target_sys


def test_main_version(capsys: CaptureFixture, version_regex: Pattern):
    # 1. ARRANGE
    args: List[str] = ["--myke-version"]

    # 2. ACT
    with mock.patch.object(target_sys, "argv", [""] + args):
        with pytest.raises(SystemExit) as pexit:
            main()

    # 3. ASSERT
    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert version_regex.search(captured.out), "invalid version"
    assert pexit.value.code == 0


def test_main_help(capsys: CaptureFixture, version_regex: Pattern):
    # 1. ARRANGE
    args: List[str] = ["--myke-help"]

    # 2. ACT
    with mock.patch.object(target_sys, "argv", [""] + args):
        with pytest.raises(SystemExit) as pexit:
            main()

    # 3. ASSERT
    captured: CaptureResult = capsys.readouterr()
    assert not captured.err
    assert captured.out
    assert pexit.value.code == 0
