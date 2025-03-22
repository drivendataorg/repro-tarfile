python := shell("cat .python-version")

# Print this help documentation
help:
    just --list

# Sync dev environment dependencies
sync:
    uv sync --all-extras

# Run linting
lint:
    ruff format --check
    ruff check

# Run formatting
format:
    ruff format
    ruff check --fix

# Run static typechecking
typecheck:
    mypy repro_tarfile.py cli --install-types --non-interactive

# Run tests
test *args:
    uv run --python {{python}} --no-editable --all-extras --no-dev --group test --isolated \
        python -I -m pytest {{args}}

# Run all tests with Python version matrix
test-all:
    for python in 3.8 3.9 3.10 3.11.3 3.11 3.12; do \
        just python=$python test; \
    done
