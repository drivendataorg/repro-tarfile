# rptar — a CLI backed by repro-tarfile

[![PyPI](https://img.shields.io/pypi/v/rptar.svg)](https://pypi.org/project/rptar/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/rptar)](https://pypi.org/project/rptar/)
[![tests](https://github.com/drivendataorg/repro-tarfile/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/drivendataorg/repro-tarfile/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/repro-tarfile/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/repro-tarfile)

**A lightweight command-line program for creating reproducible/deterministic tar archives.**

"Reproducible" or "deterministic" in this context means that the binary content of the tar archive is identical if you add files with identical binary content in the same order. It means you can reliably check equality of the contents of two tar archives by simply comparing checksums of the archive using a hash function like MD5 or SHA-256.

This package provides a command-line program named **rptar**. It is designed as a partial drop-in replacement for the ubiquitous [tar](https://linux.die.net/man/1/tar) program and implements a commonly used subset of the `tar -c` interface for creating tar archives.

For further documentation, see the ["rptar command line program"](https://github.com/drivendataorg/repro-tarfile#rptar-command-line-program) section of the repro-tarfile README.
