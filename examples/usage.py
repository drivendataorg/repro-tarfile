"""Basic usage example of repro_tarfile."""

from io import BytesIO
from pathlib import Path

from repro_tarfile import ReproducibleTarFile, TarInfo

example_dir = Path(__file__).parent

with ReproducibleTarFile.open(example_dir / "archive.tar.gz", "w:gz") as tar:
    # Use add to add a file to the archive
    tar.add(example_dir / "data.txt", arcname="data.txt")
    # Or addfile to write from a data stream to the archive
    stream = BytesIO("goodbye".encode("utf-8"))
    tarinfo = TarInfo(name="lore.txt")
    tarinfo.size = stream.getbuffer().nbytes
    tar.addfile(tarinfo, fileobj=stream)
