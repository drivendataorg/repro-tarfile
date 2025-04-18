"""A demo script that shows repro_tarfile's reproducible output in contrast with the standard
library module tarfile's nonreproducible output.
"""

import hashlib
from io import BytesIO
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from time import sleep

import repro_tarfile

example_dir = Path(__file__).parent


def create_archive(tar_module, outfile: Path):
    with tar_module.open(outfile, "w:gz") as tar:
        # Use write to add a file to the archive
        tar.add(example_dir / "data.txt", arcname="data.txt")
        # Or addfile to write data directly to the archive
        stream = BytesIO("goodbye".encode("utf-8"))
        tarinfo = repro_tarfile.TarInfo(name="lore.txt")
        tarinfo.size = stream.getbuffer().nbytes
        tar.addfile(tarinfo, fileobj=stream)


with TemporaryDirectory() as tempdir_name:
    tempdir = Path(tempdir_name)

    cases = [
        (tarfile, tempdir / "tarfile-1.tar.gz"),
        (tarfile, tempdir / "tarfile-2.tar.gz"),
        (repro_tarfile, tempdir / "repro_tarfile-1.tar.gz"),
        (repro_tarfile, tempdir / "repro_tarfile-2.tar.gz"),
    ]

    for case in cases:
        create_archive(*case)
        sleep(2)

    for _, outfile in cases:
        print(outfile.name, hashlib.md5(outfile.read_bytes()).hexdigest())
