import os
from typing import List

import myke


def test_print_text(capsys):
    test_input: str = "hello world"
    expected: str = test_input + os.linesep

    myke.print.text(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_print_lines(capsys):
    test_input: List[str] = ["hello", "world"]
    expected: str = os.linesep.join(test_input) + os.linesep

    myke.print.lines(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_print_json(capsys):
    test_input: List[str] = ["hello", "world"]
    expected: str = '["hello", "world"]' + os.linesep

    myke.print.json(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_print_table(capsys):
    test_input: List[str] = [{"hello": "world"}, {"hello": "world2"}]
    expected: str = "hello\n-------\nworld\nworld2\n"

    myke.print.table(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected


def test_print_pretty(capsys):
    test_input: str = "hello world"
    expected: str = f"'{test_input}'" + os.linesep

    myke.print.pretty(test_input)

    captured = capsys.readouterr()
    assert captured.out == expected
