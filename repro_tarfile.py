import copy
import os
import tarfile
from typing import IO, Optional

__version__ = "0.1.0"


def date_time() -> int:
    return int(os.environ.get("SOURCE_DATE_EPOCH", 0))


class ReproducibleTarFile(tarfile.TarFile):
    def addfile(self, tarinfo: tarfile.TarInfo, fileobj: Optional[IO[bytes]] = None) -> None:
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, it should be a binary file, and tarinfo.size bytes are read
        from it and added to the archive. You can create TarInfo objects
        directly, or by using gettarinfo().
        """
        tarinfo = tarinfo.replace(mtime=date_time(), deep=False)
        return super().addfile(tarinfo=tarinfo, fileobj=fileobj)


open = ReproducibleTarFile.open
