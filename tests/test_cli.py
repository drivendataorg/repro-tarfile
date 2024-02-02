import platform
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from repro_tarfile import __version__ as repro_tarfile_version
from rptar import __version__ as rptar_version
from rptar import app
from tests.utils import assert_archive_contents_equals, dir_tree_factory, file_factory

runner = CliRunner()


@pytest.fixture(autouse=True)
def copyfile_disable(monkeypatch):
    """Disable Apple's ._ file creation."""
    monkeypatch.setenv("COPYFILE_DISABLE", "1")


def test_tar_single_file(base_path):
    data_file = file_factory(base_path)

    rptar_out = base_path / "rptar.tar"
    rptar_args = ["-cf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar"
    tar_cmd = ["tar", "-cf", str(tar_out), str(data_file)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_tar_single_file_gzip(base_path):
    data_file = file_factory(base_path)

    rptar_out = base_path / "rptar.tar.gz"
    rptar_args = ["-czf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar.gz"
    tar_cmd = ["tar", "-czf", str(tar_out), str(data_file)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_tar_single_file_bz2(base_path):
    data_file = file_factory(base_path)

    rptar_out = base_path / "rptar.tar.bz2"
    rptar_args = ["-cjf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar.bz2"
    tar_cmd = ["tar", "-cjf", str(tar_out), str(data_file)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


@pytest.mark.skipif(platform.system() == "Windows", reason="xz not available on Windows")
def test_tar_single_file_xz(base_path):
    data_file = file_factory(base_path)

    rptar_out = base_path / "rptar.tar.xz"
    rptar_args = ["-cJf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar.xz"
    tar_cmd = ["tar", "-cJf", str(tar_out), str(data_file)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_tar_single_file_stdout(base_path):
    data_file = file_factory(base_path)

    rptar_args = ["-c", str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    rptar_out = base_path / "rptar.tar"
    with rptar_out.open("wb") as fp:
        fp.write(rptar_result.stdout_bytes)

    tar_out = base_path / "tar.tar"
    tar_cmd = ["tar", "-cf", str(tar_out), str(data_file)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_tar_directory(base_path):
    """Single directory, not recursive."""
    dir_tree = dir_tree_factory(base_path)

    rptar_out = base_path / "rptar.tar"
    rptar_args = ["-cf", str(rptar_out), str(dir_tree)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar"
    tar_cmd = ["tar", "-cf", str(tar_out), str(dir_tree)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_tar_directory_not_recursive(base_path):
    """Single input directory with recursive --no-recursion flag."""
    dir_tree = dir_tree_factory(base_path)

    rptar_out = base_path / "rptar.tar"
    rptar_args = ["-cf", str(rptar_out), "--no-recursion", str(dir_tree)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args

    tar_out = base_path / "tar.tar"
    tar_cmd = ["tar", "-cf", str(tar_out), "--no-recursion", str(dir_tree)]
    tar_result = subprocess.run(tar_cmd)
    assert tar_result.returncode == 0, tar_cmd

    assert_archive_contents_equals(rptar_out, tar_out)


def test_verbosity(rel_path):
    """Adjustment of verbosity with -v and -q."""
    data_file = file_factory(rel_path)
    rptar_out = rel_path / "rptar.tar"

    # Base case, should be WARNING level
    rptar_args = ["-cf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args
    assert "INFO" not in rptar_result.output
    assert "DEBUG" not in rptar_result.output

    # With -v, should be INFO level
    rptar_args = ["-cvf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args
    assert "INFO" in rptar_result.output
    assert "DEBUG" not in rptar_result.output

    # With -vv, should be DEBUG level
    rptar_args = ["-cvvf", str(rptar_out), str(data_file)]
    rptar_result = runner.invoke(app, rptar_args)
    assert rptar_result.exit_code == 0, rptar_args
    assert "INFO" in rptar_result.output
    assert "DEBUG" in rptar_result.output


def test_version():
    """With --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    output_lines = result.output.split("\n")
    assert output_lines[0].startswith("repro-tarfile ")
    assert output_lines[0].endswith(f"v{repro_tarfile_version}")
    assert output_lines[1].startswith("rptar ")
    assert output_lines[1].endswith(f"v{rptar_version}")


def test_python_dash_m_invocation():
    result = subprocess.run(
        [sys.executable, "-m", "rptar", "--help"],
        capture_output=True,
        text=True,
        universal_newlines=True,
    )
    assert result.returncode == 0
    assert "Usage: python -m rptar" in result.stdout
