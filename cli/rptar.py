from io import BytesIO
import itertools
import logging
from pathlib import Path
import sys
from typing import List, Optional

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import typer

import repro_tarfile

__version__ = "0.1.1"

app = typer.Typer()


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def version_callback(value: bool):
    if value:
        print(f"repro-tarfile v{repro_tarfile.__version__}")
        print(f"rptar v{__version__}")
        raise typer.Exit()


@app.command(context_settings={"obj": {}})
def rptar(
    in_list: Annotated[List[str], typer.Argument(help="Files to add to the archive.")],
    create: Annotated[bool, typer.Option("--create", "-c", help="Create a new archive.")],
    file: Annotated[
        Optional[str],
        typer.Option(
            "--file",
            "-f",
            help="Path of output archive file.",
        ),
    ] = None,
    gzip: Annotated[bool, typer.Option("--gzip", "-z", help="Use gzip compression.")] = False,
    bzip2: Annotated[bool, typer.Option("--bzip2", "-j", help="Use bzip2 compression.")] = False,
    xz: Annotated[
        bool, typer.Option("--xz", "-J", help="Use xz format with LZMA2 compression.")
    ] = False,
    recursion: Annotated[bool, typer.Option(help="Recurse into directories.")] = True,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            show_default=False,
            help="Use to increase log verbosity.",
        ),
    ] = 0,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Print version number and exit.",
            callback=version_callback,
        ),
    ] = None,
):
    """A lightweight replacement for `tar -c` for creating tar archives, but reproducibly/
    deterministicly. It supports a subset of common options matching tar.

    Example commands:

    \b
      rptar -czvf archive.tar.gz some_file.txt        # Archive one file
      rptar -czvf archive.tar.gz file1.txt file2.txt  # Archive two files
      rptar -czvf archive.tar.gz some_dir/*.txt       # Archive many files with glob
      rptar -czvf archive.tar.gz some_dir/            # Archive directory recursively
    """
    # Set up logger
    log_level = logging.WARNING - 10 * verbose
    logger.setLevel(log_level)
    log_handler = logging.StreamHandler()
    logger.addHandler(log_handler)
    prog_name = Path(sys.argv[0]).stem
    log_formatter = logging.Formatter(f"%(asctime)s | {prog_name} | %(levelname)s | %(message)s")
    log_handler.setFormatter(log_formatter)

    logger.debug("in_list: %s", in_list)
    logger.debug("create: %s", create)
    logger.debug("file: %s", file)
    logger.debug("gzip: %s", gzip)
    logger.debug("bzip2: %s", bzip2)
    logger.debug("xz: %s", xz)
    logger.debug("recursion: %s", recursion)

    # Check create option
    if not create:
        logger.error("Only create option is supported. Use `tar` for other operations.")
        raise typer.Exit(code=1)

    # Compression
    if sum((gzip, bzip2, xz)) > 1:
        logger.error("Only one compression option can be used at a time.")
        raise typer.Exit(code=1)
    try:
        compression = next(itertools.compress(("gz", "bz2", "xz"), (gzip, bzip2, xz)))
        logger.debug("using compression: %s", compression)
        write_mode = "w:" + compression
    except StopIteration:
        write_mode = "w"

    # Process inputs, manually recurse for logging
    in_paths = set(Path(p) for p in in_list)
    if recursion:
        for path in frozenset(in_paths):
            if path.is_dir():
                in_paths.update(path.glob("**/*"))

    if file:
        out = Path(file).resolve()
        logger.debug("writing to: %s", out)
        with repro_tarfile.open(out, write_mode) as tar:
            for path in sorted(in_paths):
                logger.info("adding: %s", path)
                tar.add(path, recursive=False)
    else:
        with BytesIO() as stream:
            with repro_tarfile.open(fileobj=stream, mode=write_mode) as tar:
                for path in sorted(in_paths):
                    logger.info("adding: %s", path)
                    tar.add(path, recursive=False)
            sys.stdout.buffer.write(stream.getvalue())


if __name__ == "__main__":
    app(prog_name="python -m rptar")
