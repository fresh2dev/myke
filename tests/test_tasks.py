import os

import pytest


def test_import_module(clean_dir):
    import myke

    myke.TASKS.clear()

    expected_file: str = os.path.join(os.getcwd(), "tasks", "python-package.py")

    myke.import_module(
        "https://www.fresh2.dev/code/r/mykefiles/raw/branch/dev/src/mykefiles/python-package.py"
    )

    assert os.path.exists(expected_file)


def test_install_module_notfound(clean_dir):
    import myke

    myke.TASKS.clear()

    expected_file: str = os.path.join(os.getcwd(), "tasks", "LICENSE")

    with pytest.raises(myke.exceptions.MykeNotFoundError):
        myke.install_module(
            "https://raw.githubusercontent.com/fresh2dev/AnyBox/main/LICENSE",
        )

    assert not os.path.exists(expected_file)
