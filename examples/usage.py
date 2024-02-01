"""Basic usage example of repro_tarfile.
"""

from io import StringIO
from pathlib import Path

from repro_tarfile import ReproducibleTarFile, TarInfo

example_dir = Path(__file__).parent

with ReproducibleTarFile.open(example_dir / "archive.tar.gz", "w:gz") as tar:
    # Use add to add a file to the archive
    tar.add(example_dir / "data.txt", arcname="data.txt")
    # Or addfile to write from a data stream to the archive
    tar.addfile(TarInfo(name="lore.txt"), fileobj=StringIO("goodbye"))
