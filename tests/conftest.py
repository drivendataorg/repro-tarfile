import os
from pathlib import Path
import sys

import pytest
from pytest_cases import fixture_union


@pytest.fixture
def abs_path(tmp_path):
    """Fixture that returns a temporary directory as an absolute Path object."""
    return tmp_path


@pytest.fixture
def rel_path(tmp_path):
    """Fixture that sets a temporary directory as the current working directory and returns a
    relative path to it."""
    orig_wd = Path.cwd()
    os.chdir(tmp_path)
    yield Path()
    os.chdir(orig_wd)


# Minimum versions with extractall filter support. Don't test abs_path if we don't have it.
EXTRACTALL_FILTER_MIN_VERSIONS = {
    (3, 8): (3, 8, 17),
    (3, 9): (3, 9, 17),
    (3, 10): (3, 10, 12),
    (3, 11): (3, 11, 4),
    (3, 12): (3, 12),
}
if sys.version_info >= EXTRACTALL_FILTER_MIN_VERSIONS[sys.version_info[:2]]:
    base_path = fixture_union("base_path", ["rel_path", "abs_path"])
else:
    base_path = fixture_union("base_path", ["rel_path"])
