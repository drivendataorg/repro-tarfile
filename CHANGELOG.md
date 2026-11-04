# Changelog — repro-tarfile

## v0.3.0 (Unreleased)

- Removed support for Python 3.8 and 3.9.
- Added support for Python 3.15.
- Fixed the type stubs importing `Self` from `typing`, which doesn't have it before Python 3.11. They now import it from `typing_extensions`.
- Changed the source distribution to contain only the package source, `pyproject.toml`, README, and LICENSE. It previously also included the CLI package, tests, and other repository files. This is a result of changing the build backend from hatchling to uv_build.

## v0.2.1 (2025-10-05)

- Added Python 3.14 to supported versions.

## v0.2.0 (2025-03-22)

- Added support for Python 3.13. ([PR #9](https://github.com/drivendataorg/repro-tarfile/pull/9))
- Added support for type checking per [PEP 561 specification](https://typing.python.org/en/latest/spec/distributing.html#packaging-typed-libraries). Types are declared with `.pyi` stubs file. ([PR #10](https://github.com/drivendataorg/repro-tarfile/pull/10))

## v0.1.0 (2024-02-02)

Initial release! 🎉
