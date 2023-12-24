import hashlib
import os
from pathlib import Path
import shutil
from tarfile import TarFile
from time import sleep
import uuid

import pytest
from pytest_cases import fixture_union

from repro_tarfile import ReproducibleTarFile


def data_factory():
    """Utility function to generate random data."""
    return str(uuid.uuid4())


def hash_file(path: Path):
    """Utility function to calculate the hash of a file's contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


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


base_path = fixture_union("base_path", ["rel_path", "abs_path"])


def test_add(base_path):
    """Test that write adds files to the archive in the expected way, i.e., we didn't break the
    basic functionality."""
    data_file = base_path / "data.txt"
    data_file.write_text(data_factory())
    data_dir = base_path / "dir"
    data_dir.mkdir()
    for i in range(3):
        (data_dir / f"{i}.txt").write_text(data_factory())

    # Create and extract ReproducibleZipFile
    repro_tarfile_file = base_path / "repro_tarfile_file.zip"
    with ReproducibleTarFile.open(repro_tarfile_file, "w") as tp:
        tp.add(data_file)
        tp.add(data_dir)
    repro_tarfile_outdir = base_path / "repro_tarfile_out"
    repro_tarfile_outdir.mkdir()
    with ReproducibleTarFile.open(repro_tarfile_file, "r") as tp:
        tp.extractall(repro_tarfile_outdir)

    # Create and extract regular TarFile for comparison
    tar_file = base_path / "tar_file.zip"
    with TarFile.open(tar_file, "w") as tp:
        tp.add(data_file)
        tp.add(data_dir)
    tar_outdir = base_path / "tar_out"
    tar_outdir.mkdir()
    with TarFile.open(tar_file, "r") as tp:
        tp.extractall(tar_outdir)

    repro_tarfile_extracted = sorted(repro_tarfile_outdir.glob("**/*"))
    tar_extracted = sorted(tar_outdir.glob("**/*"))
    assert len(repro_tarfile_extracted) == len(tar_extracted)
    for repro_tarfile_member, tar_member in zip(repro_tarfile_extracted, tar_extracted):
        assert repro_tarfile_member.relative_to(repro_tarfile_outdir) == tar_member.relative_to(
            tar_outdir
        )
        if repro_tarfile_member.is_file():
            assert tar_member.is_file()
            assert repro_tarfile_member.read_text() == tar_member.read_text()


# def test_writestr(tmp_path):
#     """Test that writestr adds files to the archive in the expected way, i.e., we didn't break the
#     basic functionality."""
#     data = data_factory()

#     with ReproducibleZipFile(tmp_path / "repro_tarfile.zip", "w") as tp:
#         tp.writestr("data.txt", data=data)

#     extract_dir = tmp_path / "extract"
#     extract_dir.mkdir()

#     with ZipFile(tmp_path / "repro_tarfile.zip", "r") as tp:
#         tp.extractall(extract_dir)

#     assert sorted(extract_dir.glob("**/*")) == [extract_dir / "data.txt"]
#     assert (extract_dir / "data.txt").read_text() == data


def test_write_same_file_different_mtime(base_path):
    """Test that writing the same file with different mtime produces the same hash."""
    data = data_factory()
    data_file = base_path / "data.txt"

    data_file.write_text(data)
    with ReproducibleTarFile.open(base_path / "tar1.tar", "w") as tp:
        tp.add(data_file)

    sleep(2)

    data_file.write_text(data)
    with ReproducibleTarFile.open(base_path / "tar2.tar", "w") as tp:
        tp.add(data_file)

    assert hash_file(base_path / "tar1.tar") == hash_file(base_path / "tar2.tar")


# def test_write_same_file_different_mtime_source_date_epoch(base_path, monkeypatch):
#     """Test that writing the same file at different times with SOURCE_DATE_EPOCH set produces the
#     same hash."""
#     monkeypatch.setenv("SOURCE_DATE_EPOCH", "1691732367")
#     data = data_factory()
#     data_file = base_path / "data.txt"

#     data_file.write_text(data)
#     with ReproducibleZipFile(base_path / "zip1.zip", "w") as tp:
#         tp.write(data_file)

#     sleep(2)

#     data_file.write_text(data)
#     with ReproducibleZipFile(base_path / "zip2.zip", "w") as tp:
#         tp.write(data_file)

#     assert hash_file(base_path / "zip1.zip") == hash_file(base_path / "zip2.zip")


# def test_write_same_file_different_mtime_string_input(rel_path):
#     """Test that writing the same file with different mtime produces the same hash, using string
#     inputs instead of Path."""
#     data = data_factory()
#     data_file = rel_path / "data.txt"

#     data_file.write_text(data)
#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.write("data.txt")

#     sleep(2)

#     data_file.write_text(data)
#     with ReproducibleZipFile(rel_path / "zip2.zip", "w") as tp:
#         tp.write("data.txt")

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")


# def test_write_same_file_different_mtime_arcname(base_path):
#     """Test that writing the same file with different mtime produces the same hash."""
#     data = data_factory()
#     data_file = base_path / "data.txt"

#     data_file.write_text(data)
#     with ReproducibleZipFile(base_path / "zip1.zip", "w") as tp:
#         tp.write(data_file, arcname="lore.txt")

#     sleep(2)

#     data_file.write_text(data)
#     with ReproducibleZipFile(base_path / "zip2.zip", "w") as tp:
#         tp.write(data_file, arcname="lore.txt")

#     assert hash_file(base_path / "zip1.zip") == hash_file(base_path / "zip2.zip")


# def test_write_same_directory_different_mtime(base_path):
#     data_list = [data_factory() for _ in range(3)]
#     data_dir = base_path / "dir"

#     data_dir.mkdir()
#     for data in data_list:
#         (data_dir / f"{data}.txt").write_text(data)
#     with ReproducibleZipFile(base_path / "zip1.zip", "w") as tp:
#         tp.write(data_dir)
#         for root, dirs, files in os.walk(data_dir):
#             for d in dirs:
#                 tp.write(Path(root) / d)
#             for f in files:
#                 tp.write(Path(root) / f)

#     sleep(2)

#     shutil.rmtree(data_dir)
#     data_dir.mkdir()
#     for data in data_list:
#         (data_dir / f"{data}.txt").write_text(data)
#     with ReproducibleZipFile(base_path / "zip2.zip", "w") as tp:
#         tp.write(data_dir)
#         for root, dirs, files in os.walk(data_dir):
#             for d in dirs:
#                 tp.write(Path(root) / d)
#             for f in files:
#                 tp.write(Path(root) / f)

#     assert hash_file(base_path / "zip1.zip") == hash_file(base_path / "zip2.zip")


# def test_write_same_directory_different_mtime_string_input(rel_path):
#     data_list = [data_factory() for _ in range(3)]
#     data_dir = rel_path / "dir"

#     data_dir.mkdir()
#     for data in data_list:
#         (data_dir / f"{data}.txt").write_text(data)
#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.write(data_dir.name)
#         for root, dirs, files in os.walk(data_dir):
#             for d in dirs:
#                 tp.write(os.path.join(root, d))
#             for f in files:
#                 tp.write(os.path.join(root, f))

#     sleep(2)

#     shutil.rmtree(data_dir)
#     data_dir.mkdir()
#     for data in data_list:
#         (data_dir / f"{data}.txt").write_text(data)
#     with ReproducibleZipFile("zip2.zip", "w") as tp:
#         tp.write(data_dir.name)
#         for root, dirs, files in os.walk(data_dir):
#             for d in dirs:
#                 tp.write(os.path.join(root, d))
#             for f in files:
#                 tp.write(os.path.join(root, f))

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")


# def test_writestr_same_data_different_mtime(rel_path):
#     """Test that using writestr with the same data at different times produces the same hash."""
#     data = data_factory()

#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.writestr("data.txt", data=data)

#     sleep(2)

#     with ReproducibleZipFile(rel_path / "zip2.zip", "w") as tp:
#         tp.writestr("data.txt", data=data)

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")


# def test_writestr_same_data_different_mtime_zipinfo_input(rel_path):
#     """Test that using writestr with the same data at different times produces the same hash."""
#     data = data_factory()
#     data_file = rel_path / "data.txt"

#     data_file.write_text(data)
#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.writestr(ZipInfo.from_file(data_file), data=data)

#     sleep(2)

#     data_file.write_text(data)
#     with ReproducibleZipFile(rel_path / "zip2.zip", "w") as tp:
#         tp.writestr(ZipInfo.from_file(data_file), data=data)

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")


# def test_writestr_same_data_different_mtime_source_date_epoch(rel_path, monkeypatch):
#     """Test that using writestr with the same data at different times with SOURCE_DATE_EPOCH set
#     produces the same hash."""
#     monkeypatch.setenv("SOURCE_DATE_EPOCH", "1691732367")
#     data = data_factory()

#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.writestr("data.txt", data=data)

#     sleep(2)

#     with ReproducibleZipFile(rel_path / "zip2.zip", "w") as tp:
#         tp.writestr("data.txt", data=data)

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")


# def test_mkdir(rel_path):
#     with ReproducibleZipFile(rel_path / "zip1.zip", "w") as tp:
#         tp.mkdir("dir")

#     sleep(2)

#     with ReproducibleZipFile(rel_path / "zip2.zip", "w") as tp:
#         tp.mkdir("dir")

#     assert hash_file(rel_path / "zip1.zip") == hash_file(rel_path / "zip2.zip")
