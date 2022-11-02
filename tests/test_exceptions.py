import pytest

from myke import sh
from myke.exceptions import CalledProcessError


def test_called_process_error():
    with pytest.raises(CalledProcessError) as excinfo:
        sh("hello world")

    assert excinfo.value
    e: Exception = excinfo.value
    assert "stdout:" in str(e)
    assert "stderr:" in str(e)
