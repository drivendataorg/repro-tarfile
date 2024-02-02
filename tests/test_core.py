from io import StringIO
import platform
import sys
from tarfile import TarFile, TarInfo
from time import sleep

try:
    from time import tzset
except ImportError:
    tzset = None

import pytest

from repro_tarfile import ReproducibleTarFile, mtime
from tests.utils import (
    assert_archive_contents_equals,
    data_factory,
    dir_tree_factory,
    file_factory,
    hash_file,
    umask,
)


def test_add_dir_tree_mtime(base_path):
    """Archiving a directory tree works with different modified time."""
    dir_tree = dir_tree_factory(base_path)

    # Create base ReproducibleTarFile archive
    rptf_arc1 = base_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Create regular TarFile archive for comparison
    tf_arc1 = base_path / "tf_arc1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Sleep to update modified times, change permissions
    sleep(2)
    for path in dir_tree.glob("**/*"):
        path.touch()

    # Create second ReproducibleTarFile archive after delay
    rptf_arc2 = base_path / "tptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Create second regular TarFile archive for comparison after delay
    tf_arc2 = base_path / "tf_arc2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_dir_tree_mode(base_path):
    """Archiving a directory tree works with different permission modes."""
    with umask(0o022):
        dir_tree = dir_tree_factory(base_path)

    # Create base ReproducibleTarFile archive
    rptf_arc1 = base_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Create regular TarFile archive for comparison
    tf_arc1 = base_path / "zipfile1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Change permissions
    with umask(0o002) as mask:
        dir_tree.chmod(mode=0o777 ^ mask)
        for path in dir_tree.glob("**/*"):
            if path.is_file():
                path.chmod(mode=0o666 ^ mask)
            else:
                path.chmod(mode=0o777 ^ mask)

    # Create second ReproducibleTarFile archive using files with new permissions
    rptf_arc2 = base_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # Create second regular TarFile archive for comparison using files with new permissions
    tf_arc2 = base_path / "zipfile2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(path)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    if platform.system() != "Windows":
        # Windows doesn't seem to actually make them different
        assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_dir_tree_string_paths(rel_path):
    """Archiving a directory tree with string path names."""
    dir_tree = dir_tree_factory(rel_path)

    # Create base ReproducibleTarFile archive
    rptf_arc1 = rel_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(str(path))

    # Create regular TarFile archive for comparison
    tf_arc1 = rel_path / "zipfile1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(str(path))

    # Update modified times
    sleep(2)
    for path in dir_tree.glob("**/*"):
        path.touch()

    # Create second ReproducibleTarFile archive after delay
    rptf_arc2 = rel_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(str(path))

    # Create second regular TarFile archive for comparison after delay
    tf_arc2 = rel_path / "zipfile2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        for path in sorted(dir_tree.glob("**/*")):
            tp.add(str(path))

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_single_file(base_path):
    """Writing the same file with different mtime produces the same hash."""
    data_file = file_factory(base_path)

    rptf_arc1 = base_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        tp.add(data_file)

    tf_arc1 = base_path / "tf_arc1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        tp.add(data_file)

    print(data_file.stat())
    sleep(2)
    data_file.touch()
    print(data_file.stat())

    rptf_arc2 = base_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        tp.add(data_file)

    tf_arc2 = base_path / "tf_arc2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        tp.add(data_file)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


@pytest.mark.skipif(tzset is None, reason="tzset not available")
def test_mtime_not_affected_by_timezone(monkeypatch):
    monkeypatch.setenv("TZ", "America/Chicago")
    tzset()
    dt1 = mtime()
    monkeypatch.setenv("TZ", "America/Los_Angeles")
    tzset()
    dt2 = mtime()

    assert dt1 == dt2


def test_add_single_file_gz(base_path):
    """Writing the same file with different mtime produces the same hash with gzip compression."""
    data_file = file_factory(base_path)

    rptf_arc1 = base_path / "rptf_arc1.tar.gz"
    with ReproducibleTarFile.open(rptf_arc1, "w:gz") as tp:
        tp.add(data_file)

    tf_arc1 = base_path / "tf_arc1.tar.gz"
    with TarFile.open(tf_arc1, "w:gz") as tp:
        tp.add(data_file)

    print(data_file.stat())
    sleep(2)
    data_file.touch()
    print(data_file.stat())

    rptf_arc2 = base_path / "rptf_arc2.tar.gz"
    with ReproducibleTarFile.open(rptf_arc2, "w:gz") as tp:
        tp.add(data_file)

    tf_arc2 = base_path / "tf_arc2.tar.gz"
    with TarFile.open(tf_arc2, "w:gz") as tp:
        tp.add(data_file)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_single_file_bz2(base_path):
    """Writing the same file with different mtime produces the same hash with bzip2 compression."""
    data_file = file_factory(base_path)

    rptf_arc1 = base_path / "rptf_arc1.tar.bz2"
    with ReproducibleTarFile.open(rptf_arc1, "w:bz2") as tp:
        tp.add(data_file)

    tf_arc1 = base_path / "tf_arc1.tar.bz2"
    with TarFile.open(tf_arc1, "w:bz2") as tp:
        tp.add(data_file)

    print(data_file.stat())
    sleep(2)
    data_file.touch()
    print(data_file.stat())

    rptf_arc2 = base_path / "rptf_arc2.tar.bz2"
    with ReproducibleTarFile.open(rptf_arc2, "w:bz2") as tp:
        tp.add(data_file)

    tf_arc2 = base_path / "tf_arc2.tar.bz2"
    with TarFile.open(tf_arc2, "w:bz2") as tp:
        tp.add(data_file)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_single_file_xz(base_path):
    """Writing the same file with different mtime produces the same hash with xz format /
    LCMA2 compression.
    """
    data_file = file_factory(base_path)

    rptf_arc1 = base_path / "rptf_arc1.tar.xz"
    with ReproducibleTarFile.open(rptf_arc1, "w:xz") as tp:
        tp.add(data_file)

    tf_arc1 = base_path / "tf_arc1.tar.xz"
    with TarFile.open(tf_arc1, "w:xz") as tp:
        tp.add(data_file)

    print(data_file.stat())
    sleep(2)
    data_file.touch()
    print(data_file.stat())

    rptf_arc2 = base_path / "rptf_arc2.tar.xz"
    with ReproducibleTarFile.open(rptf_arc2, "w:xz") as tp:
        tp.add(data_file)

    tf_arc2 = base_path / "tf_arc2.tar.xz"
    with TarFile.open(tf_arc2, "w:xz") as tp:
        tp.add(data_file)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_single_file_source_date_epoch(base_path, monkeypatch):
    """Writing the same file with different mtime with SOURCE_DATE_EPOCH set produces the
    same hash."""

    data_file = file_factory(base_path)

    arc_base = base_path / "base.tar"
    with ReproducibleTarFile.open(arc_base, "w") as tp:
        tp.add(data_file)

    # With SOURCE_DATE_EPOCH set
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1691732367")
    arc_sde1 = base_path / "with_sde1.tar"
    with ReproducibleTarFile.open(arc_sde1, "w") as tp:
        tp.add(data_file)

    sleep(2)
    data_file.touch()

    arc_sde2 = base_path / "with_sde2.tar"
    with ReproducibleTarFile.open(arc_sde2, "w") as tp:
        tp.add(data_file)

    # All four archives should have identical content
    assert_archive_contents_equals(arc_base, arc_sde1)
    assert_archive_contents_equals(arc_base, arc_sde2)

    # Base archive hash should match neither, two archives with SOURCE_DATE_EPOCH should match
    assert hash_file(arc_base) != hash_file(arc_sde1)
    assert hash_file(arc_sde1) == hash_file(arc_sde2)


def test_add_single_file_file_mode_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_FILE_MODE environment variable works."""

    with umask(0o002):
        # Expect 664
        data_file = file_factory(rel_path)

    monkeypatch.setenv("REPRO_TARFILE_FILE_MODE", "600")  # rw-------

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(data_file)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        mode = tp.getmember(data_file.name).mode & 0o777

    assert mode == 0o600, (oct(mode), oct(0o600))


def test_add_single_dir_dir_mode_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_DIR_MODE environment variable works."""

    with umask(0o002):
        # Expect 775
        dir_path = rel_path / data_factory()
        dir_path.mkdir()

    monkeypatch.setenv("REPRO_TARFILE_DIR_MODE", "700")  # rwx------

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(dir_path)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        if sys.version_info >= (3, 9):
            expected_name = dir_path.name + "/"
        else:
            expected_name = dir_path.name
        mode = tp.getmember(expected_name).mode & 0o777

    assert mode == 0o700, (oct(mode), oct(0o700))


def test_add_single_file_uid_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_UID environment variable works."""

    data_file = file_factory(rel_path)

    monkeypatch.setenv("REPRO_TARFILE_UID", "9999")

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(data_file)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        uid = tp.getmember(data_file.name).uid

    assert uid == 9999


def test_add_single_file_gid_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_GID environment variable works."""

    data_file = file_factory(rel_path)

    monkeypatch.setenv("REPRO_TARFILE_GID", "9999")

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(data_file)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        gid = tp.getmember(data_file.name).gid

    assert gid == 9999


def test_add_single_file_uname_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_UNAME environment variable works."""

    data_file = file_factory(rel_path)

    monkeypatch.setenv("REPRO_TARFILE_UNAME", "testuser123")

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(data_file)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        uname = tp.getmember(data_file.name).uname

    assert uname == "testuser123"


def test_add_single_file_gname_env_var(rel_path, monkeypatch):
    """REPRO_TARFILE_GNAME environment variable works."""

    data_file = file_factory(rel_path)

    monkeypatch.setenv("REPRO_TARFILE_GNAME", "testgroup123")

    arc_path = rel_path / "archive.tar"
    with ReproducibleTarFile.open(arc_path, "w") as tp:
        tp.add(data_file)

    with TarFile.open(arc_path, "r") as tp:
        print(tp.getmembers())
        gname = tp.getmember(data_file.name).gname

    assert gname == "testgroup123"


def test_add_single_file_string_paths(rel_path):
    """Writing the same file with different mtime produces the same hash, using string inputs
    instead of Path."""
    data_file = file_factory(rel_path)
    file_name = data_file.name
    assert isinstance(file_name, str)

    rptf_arc1 = rel_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        tp.add(file_name)

    tf_arc1 = rel_path / "tf_arc1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        tp.add(file_name)

    sleep(2)
    data_file.touch()

    rptf_arc2 = rel_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        tp.add(file_name)

    tf_arc2 = rel_path / "tf_arc2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        tp.add(file_name)

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_add_single_file_arcname(base_path):
    """Writing a single file with explicit arcname."""
    data_file = file_factory(base_path)

    rptf_arc1 = base_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        tp.add(data_file, arcname="lore.txt")

    tf_arc1 = base_path / "tf_arc1.tar"
    with TarFile.open(tf_arc1, "w") as tp:
        tp.add(data_file, arcname="lore.txt")

    sleep(2)
    data_file.touch()

    rptf_arc2 = base_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        tp.add(data_file, arcname="lore.txt")

    tf_arc2 = base_path / "tf_arc2.tar"
    with TarFile.open(tf_arc2, "w") as tp:
        tp.add(data_file, arcname="lore.txt")

    # All four archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc1)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)
    assert_archive_contents_equals(rptf_arc1, tf_arc2)

    # ReproducibleTarFile hashes should match; TarFile hashes should not
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
    assert hash_file(tf_arc1) != hash_file(tf_arc2)


def test_addfile(tmp_path):
    """addfile works as expected"""
    data = data_factory()

    rptf_arc1 = tmp_path / "rptf_arc1.tar"
    with ReproducibleTarFile.open(rptf_arc1, "w") as tp:
        tp.addfile(TarInfo("data.txt"), fileobj=StringIO(data))

    tf_arc = tmp_path / "tf_arc.tar"
    with TarFile.open(tf_arc, "w") as tp:
        tp.addfile(TarInfo("data.txt"), fileobj=StringIO(data))

    sleep(2)

    rptf_arc2 = tmp_path / "rptf_arc2.tar"
    with ReproducibleTarFile.open(rptf_arc2, "w") as tp:
        tp.addfile(TarInfo("data.txt"), fileobj=StringIO(data))

    # All three archives should have identical content
    assert_archive_contents_equals(rptf_arc1, tf_arc)
    assert_archive_contents_equals(rptf_arc1, rptf_arc2)

    # ReproducibleTarFile hashes should match
    assert hash_file(rptf_arc1) == hash_file(rptf_arc2)
