from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
from tarfile import TarFile
from tempfile import TemporaryDirectory


class _DataFactory:
    """Utility function to generate a unique data string using an incrementing counter."""

    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        out = f"{self.counter:04d}"
        self.counter += 1
        return out


data_factory = _DataFactory()


def file_factory(parent_dir: Path) -> Path:
    """Utility function to generate a file with random data."""
    path = parent_dir / f"{data_factory()}.txt"
    path.write_text(data_factory())
    return path


def dir_tree_factory(parent_dir: Path):
    """Utility function to generate a directory tree containing files with random data."""
    root_dir = parent_dir / data_factory()
    root_dir.mkdir()

    for _ in range(3):
        file_factory(root_dir)

    sub_dir = root_dir / "sub_dir"
    sub_dir.mkdir()

    for _ in range(3):
        file_factory(sub_dir)

    return root_dir


@contextmanager
def umask(mask: int):
    """Utility context manager to temporarily set umask to a new value."""
    old_mask = os.umask(mask)
    yield mask
    os.umask(old_mask)


def hash_file(path: Path):
    """Utility function to calculate the hash of a file's contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def assert_archive_contents_equals(arc1: Path, arc2: Path):
    with TemporaryDirectory() as outdir1, TemporaryDirectory() as outdir2:
        try:
            with TarFile.open(arc1, "r") as tp:
                tp.extractall(outdir1, filter="tar")
            with TarFile.open(arc2, "r") as tp:
                tp.extractall(outdir2, filter="tar")
        except TypeError:
            with TarFile.open(arc1, "r") as tp:
                tp.extractall(outdir1)
            with TarFile.open(arc2, "r") as tp:
                tp.extractall(outdir2)

        extracted1 = sorted(Path(outdir1).glob("**/*"))
        extracted2 = sorted(Path(outdir2).glob("**/*"))

        assert [p.relative_to(outdir1) for p in extracted1] == [
            p.relative_to(outdir2) for p in extracted2
        ]
        for arc1_member, arc2_member in zip(extracted1, extracted2):
            assert arc1_member.is_file() == arc2_member.is_file()
            if arc1_member.is_file():
                assert hash_file(arc1_member) == hash_file(arc2_member)
