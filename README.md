# repro-tarfile

[![PyPI](https://img.shields.io/pypi/v/repro-tarfile.svg)](https://pypi.org/project/repro-tarfile/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/repro-tarfile.svg)](https://anaconda.org/conda-forge/repro-tarfile)
[![conda-forge feedstock](https://img.shields.io/badge/conda--forge-feedstock-yellowgreen)](https://github.com/conda-forge/repro-tarfile-feedstock)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/repro-tarfile)](https://pypi.org/project/repro-tarfile/)
[![tests](https://github.com/drivendataorg/repro-tarfile/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/drivendataorg/repro-tarfile/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/repro-tarfile/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/repro-tarfile)

> [!IMPORTANT]
> repro-tarfile is still a work-in-progress and not yet actually available for use

**A tiny, zero-dependency replacement for Python's `tarfile` library for creating reproducible/deterministic tar archives.**

"Reproducible" or "deterministic" in this context means that the binary content of the tar archive is identical if you add files with identical binary content in the same order. It means you can reliably check equality of the contents of two tar archives by simply comparing checksums of the archive using a hash function like MD5 or SHA-256.

This Python package provides a `ReproducibleTarFile` class that works exactly like [`tarfile.TarFile`](https://docs.python.org/3/library/tarfile.html#tarfile-objects) from the Python standard library, except that certain file metadata are set to fixed values. See ["How does repro-tarfile work?"](#how-does-repro-tarfile-work) below for details.

You can also optionally install a command-line program, **rptar**. See ["rptar command line program"](#rptar-command-line-program) below for more information.

_Looking to create reproducible/deterministic ZIP archives? Check out our sister package, [repro-zipfile](https://github.com/drivendataorg/repro-zipfile)!_

## Installation

repro-tarfile is available from PyPI. To install, run:

```bash
pip install repro-tarfile
```

It is also available from conda-forge. To install, run:

```bash
conda install repro-tarfile -c conda-forge
```

## Usage

Simply `import repro_tarfile` and use it in the same way you would use regular [`tarfile`](https://docs.python.org/3/library/tarfile.html) from the Python standard library.

```python
import repro_tarfile

with repro_tarfile.open("archive.tar.gz", "w:gz") as tar:
    tar.add("examples/data.txt", arcname="data.txt")
```

Note that files must be written to the archive in the same order to reproduce an identical archive. Be aware that functions that like `os.listdir`, `os.glob`, `Path.iterdir`, and `Path.glob` return files in a nondeterministic order—you should call `sorted` on their returned values first.

See [`examples/usage.py`](./examples/usage.py) for an example script that you can run, and [`examples/demo_vs_tarfile.py`](./examples/demo_vs_tarfile.py) for a demonstration in contrast with the standard library's tarfile module.

For more advanced usage, such as customizing the fixed metadata values, see the subsections under ["How does repro-tarfile work?"](#how-does-repro-tarfile-work).

## rptar command-line program

[![PyPI](https://img.shields.io/pypi/v/rptar.svg)](https://pypi.org/project/rptar/)

You can optionally install a lightweight command-line program, **rptar**. This includes an additional dependency on the [typer](https://typer.tiangolo.com/) CLI framework. You can install it either directly or using the `cli` extra with repro-tarfile. We recommend you use [pipx](https://github.com/pypa/pipx) for Python CLIs in isolated environments.

```bash
pipx install rptar
# or
pipx install repro-tarfile[cli]
```

rptar is designed to a partial drop-in replacement ubiquitous [tar](https://linux.die.net/man/1/tar) program. Use `rptar --help` to see the documentation. Here are some usage examples:

```bash
# Archive a single file
rptar archive.zip examples/data.txt
# Archive multiple files
rptar archive.zip examples/data.txt README.md
# Archive multiple files with a shell glob
rptar archive.zip examples/*.py
# Archive a directory recursively
rptar -r archive.zip examples
```

In addition to the fixed file metadata done by repro-tarfile, rptar will also always sort all paths being written.

## How does repro-tarfile work?

Tar archives are not normally reproducible even when containing files with identical content because of file metadata. In particular, the usual culprits are:

1. Last-modified timestamps
2. File-system permissions (mode)
3. File owner user and group

`repro_tarfile.ReproducibleTarFile` is a subclass of `tarfile.TarFile` that overrides the `addfile` method (which is also used interally by `add`) with a version that set the above metadata to fixed values. Note that repro-tarfile does not modify the original files—only the metadata written to the archive.

You can effectively reproduce what `ReproducibleTarFile` does with something like this:

```python
from tarfile import TarFile

with TarFile.open("archive.tar.gz", "w:gz") as tar:
    # Use write to add a file to the archive
    tar.add("examples/data.txt", arcname="data.txt")
    tarinfo = tar.getmember("data.txt")

```

It's not hard to do, but we believe `ReproducibleTarFile` is sufficiently more convenient to justify a small package!

See the next two sections for more details about the replacement metadata values and how to customize them.

### Fixed metadata values

Here's a quick reference table of the fixed metadata values. You can use the associated environment variable to override a value.

| Metadata field          | Default                               | Environment variable      |
|-------------------------|---------------------------------------|---------------------------|
| Last modified timestamp | `315532800` (1980-01-01 00:00:00 UTC) | `SOURCE_DATE_EPOCH`       |
| File mode               | `644` (rw-r--r--)                     | `REPRO_TARFILE_FILE_MODE` |
| Directory mode          | `755` (rwxr-xr-x)                     | `REPRO_TARFILE_DIR_MODE`  |
| Owner user ID           | `0`                                   | `REPRO_TARFILE_UID`       |
| Owner group ID          | `0`                                   | `REPRO_TARFILE_GID`       |
| Owner user name         | empty string                          | `REPRO_TARFILE_UNAME`     |
| Owner group name        | empty string                          | `REPRO_TARFILE_GNAME`     |

For deeper explanations, see below.

#### Last-modified timestamps

Tar archives store the last-modified timestamps of files and directories. The default fixed value used by repro-tarfile is 315532800, which corresponds to 1980-01-01 00:00:00 UTC.

You can customize this value with the `SOURCE_DATE_EPOCH` environment variable. If set, it will be used as the fixed value instead. This should be an integer corresponding to the [Unix epoch time](https://en.wikipedia.org/wiki/Unix_time) of the timestamp you want to set, e.g., `1704067230` for 2024-01-01 00:00:00 UTC. `SOURCE_DATE_EPOCH` is a [standard](https://reproducible-builds.org/docs/source-date-epoch/) created by the [Reproducible Builds project](https://reproducible-builds.org/) for software distributions.

### File-system permissions

Tar archives store the file-system permissions of files and directories. The default permissions set for new files or directories often can be different across different systems or users without any intentional choices being made. (These default permissions are controlled by something called [`umask`](https://en.wikipedia.org/wiki/Umask).) repro-tarfile will set these to fixed values. By default, the fixed values are `0o644` (`rw-r--r--`) for files and `0o755` (`rwxr-xr-x`) for directories, which matches the common default `umask` of `0o022` for root users on Unix systems. (The [`0o` prefix](https://docs.python.org/3/reference/lexical_analysis.html#integers) is how you can write an octal—i.e., base 8—integer literal in Python.)

You can customize these values using the environment variables `REPRO_ZIPFILE_FILE_MODE` and `REPRO_ZIPFILE_DIR_MODE`. They should be in three-digit octal [Unix numeric notation](https://en.wikipedia.org/wiki/File-system_permissions#Numeric_notation), e.g., `644` for `rw-r--r--`.

### File owner user and group

In typical file systems, every file and directory has an owner. Tar archives record the user and group information of the owner. If different users or systems are generating identical files and then archiving them, the owner information will likely be different. By default, repro-tarfile uses user and group IDs values of `0`, and empty strings for the user and group names. These are the standard values recommended by the [Reproducible Builds project](https://reproducible-builds.org/docs/archives/#users-groups-and-numeric-ids).

You can customize the user and group IDs using the environment variables `REPRO_TARFILE_UID` and `REPRO_TARFILE_GID`. The values should be integers. You can customize the user and group names using the environment variables `REPRO_TARFILE_UNAME` and `REPRO_TARFILE_GNAME`.

## Why care about reproducible tar archives?

Tar archives are often useful when dealing with a set of multiple files, especially if the files are large and can be compressed. Creating reproducible tar archives is often useful for:

- **Building a software package.** This is a development best practice to make it easier to verify distributed software packages. See the [Reproducible Builds project](https://reproducible-builds.org/) for more explanation.
- **Working with data.** Verify that your data pipeline produced the same outputs, and avoid further reprocessing of identical data.
- **Packaging machine learning model artifacts.** Manage model artifact packages more effectively by knowing when they contain identical models.

## Related Tools and Alternatives

- https://diffoscope.org/
    - Can do a rich comparison of archive files and show what specifically differs
- https://salsa.debian.org/reproducible-builds/strip-nondeterminism
    - Perl library for removing nondeterministic metadata from file archives
