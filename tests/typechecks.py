from io import BytesIO
from tarfile import TarFile

from typing_extensions import assert_type

import repro_tarfile
from repro_tarfile import ReproducibleTarFile, TarInfo

assert_type(repro_tarfile.__version__, str)

# open
assert_type(repro_tarfile.open("archive.tar"), TarFile)
assert_type(repro_tarfile.open("archive.tar", "w"), TarFile)
assert_type(repro_tarfile.open("archive.tar.gz", "w:gz", compresslevel=6), TarFile)
assert_type(repro_tarfile.open("archive.tar.xz", "w:xz", preset=6), TarFile)
assert_type(ReproducibleTarFile.open("archive.tar", "w"), ReproducibleTarFile)

# gzopen
assert_type(ReproducibleTarFile.gzopen("archive.tar.gz"), ReproducibleTarFile)
assert_type(ReproducibleTarFile.gzopen("archive.tar.gz", "w"), ReproducibleTarFile)

# add and addfile
with ReproducibleTarFile.open("archive.tar", "w") as tf:
    assert_type(tf, ReproducibleTarFile)
    tf.add("file.txt")
    tf.addfile(TarInfo("file.txt"), BytesIO(b"data"))
    tf.addfile(TarInfo("dir"))
