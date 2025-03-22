from gzip import _ReadableFileobj as _GzipReadableFileobj
from tarfile import TarFile
from tarfile import TarInfo as TarInfo

from _typeshed import Incomplete, StrOrBytesPath

__all__ = ["open", "ReproducibleTarFile", "TarInfo"]

class ReproducibleTarFile(TarFile):
    @classmethod
    def gzopen(
        cls,
        name: StrOrBytesPath | None,
        mode: str = "r",
        fileobj: _GzipReadableFileobj | None = None,
        compresslevel: int = 9,
        **kwargs,
    ) -> None: ...
    def addfile(self, tarinfo: TarInfo, fileobj: Incomplete | None = None) -> None: ...

open: Incomplete
