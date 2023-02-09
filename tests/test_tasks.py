import os

import pytest


def test_import_module(clean_dir):
    import myke

    myke.TASKS.clear()

    file_name: str = "py_pkg.py"
    expected_file: str = os.path.join(os.getcwd(), "tasks", file_name)

    myke.import_module(
        "https://codeberg.org/fresh2dev/mykefiles/raw/branch/dev/src/mykefiles/"
        + file_name,
    )
    with pytest.raises(FileExistsError):
        myke.install_module(
            "https://codeberg.org/fresh2dev/mykefiles/raw/branch/dev/src/mykefiles/"
            + file_name,
            fail_if_exists=True,
        )

    os.environ["MYKE_UPDATE_MODULES"] = "1"

    myke.install_module(
        "https://codeberg.org/fresh2dev/mykefiles/raw/branch/dev/src/mykefiles/"
        + file_name,
        fail_if_exists=True,
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
