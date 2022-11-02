import pytest

from myke.utils import is_version


@pytest.mark.parametrize(
    "txt",
    [
        "1",
        "1.0",
        "1.0.0",
        "1.0.0a1",
        "1.0.0b1",
        "1.0.0rc1",
        "v1",
        "v1.0",
        "v1.0.0",
        "v1.0.0a1",
        "v1.0.0b1",
        "v1.0.0rc1",
    ],
)
def test_is_version(txt: str):
    assert is_version(txt)


@pytest.mark.parametrize(
    "txt",
    [
        "a",
        "a.b",
        "a.b.c",
    ],
)
def test_not_is_version(txt: str):
    assert not is_version(txt)
