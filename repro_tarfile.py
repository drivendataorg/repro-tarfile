import builtins
import contextlib
import copy
import datetime
import os
from tarfile import CompressionError, ReadError, TarFile, TarInfo
from typing import IO, Optional

__version__ = "0.1.0"

__all__ = [
    "open",
    "ReproducibleTarFile",
    "TarInfo",
]


def mtime() -> int:
    """Returns mtime value used to force overwrite on all TarInfo objects. Defaults to
    315532800 (corresponding to 1980-01-01 00:00:00 UTC). You can set this with the environment
    variable SOURCE_DATE_EPOCH as an integer value representing seconds since Epoch.
    """
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH", None)
    if source_date_epoch is not None:
        return int(source_date_epoch)
    return int(datetime.datetime(1980, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())


def file_mode() -> int:
    """Returns the file permissions mode value used to force overwrite on all TarInfo objects.
    Defaults to 0o644 (rw-r--r--). You can set this with the environment variable
    REPRO_TARFILE_FILE_MODE. It should be in the Unix standard three-digit octal representation
    (e.g., '644').
    """
    file_mode_env = os.environ.get("REPRO_TARFILE_FILE_MODE", None)
    if file_mode_env is not None:
        return int(file_mode_env, 8)
    return 0o644


def dir_mode() -> int:
    """Returns the directory permissions mode value used to force overwrite on all TarInfo objects.
    Defaults to 0o755 (rwxr-xr-x). You can set this with the environment variable
    REPRO_TARFILE_DIR_MODE. It should be in the Unix standard three-digit octal representation
    (e.g., '755').
    """
    dir_mode_env = os.environ.get("REPRO_TARFILE_DIR_MODE", None)
    if dir_mode_env is not None:
        return int(dir_mode_env, 8)
    return 0o755


def uid() -> int:
    """Returns the user id value used to force overwrite on all TarInfo objects. Defaults to 0.
    You can set this with the environment variable REPRO_TARFILE_UID.
    """
    uid_env = os.environ.get("REPRO_TARFILE_UID", None)
    if uid_env is not None:
        return int(uid_env)
    return 0


def gid() -> int:
    """Returns the group id value used to force overwrite on all TarInfo objects. Defaults to 0.
    You can set this with the environment variable REPRO_TARFILE_GID.
    """
    gid_env = os.environ.get("REPRO_TARFILE_GID", None)
    if gid_env is not None:
        return int(gid_env)
    return 0


def uname() -> str:
    """Returns the user name value used to force overwrite on all TarInfo objects. Defaults to
    empty string. You can set this with the environment variable REPRO_TARFILE_UNAME.
    """
    uname_env = os.environ.get("REPRO_TARFILE_UNAME", None)
    if uname_env is not None:
        return uname_env
    return ""


def gname() -> str:
    """Returns the group name value used to force overwrite on all TarInfo objects. Defaults to
    empty string. You can set this with the environment variable REPRO_TARFILE_GNAME.
    """
    gname_env = os.environ.get("REPRO_TARFILE_GNAME", None)
    if gname_env is not None:
        return gname_env
    return ""


_NO_TARFILE_ATTR = object()


@contextlib.contextmanager
def _temporarily_delete_tarfile_attr(tarinfo: TarInfo):
    """Context manager for temporarily deleting the tarfile attribute from a TarInfo object.

    For some reason, TarInfo objects returned by TarFile.gettarinfo get assigned a 'tarfile'
    attribute with a reference ot the TarInfo object.

    https://github.com/python/cpython/blob/f7c05d7ad3075a1dbeed86b6b12903032e4afba6/Lib/tarfile.py#L2033

    The TarInfo can have IO streams that prevent deepcopy. This context manager temporarily deletes
    the tarfile attribute so that we can do a deepcopy successfully.
    """
    tarfile_attr = getattr(tarinfo, "tarfile", _NO_TARFILE_ATTR)
    if tarfile_attr is not _NO_TARFILE_ATTR:
        delattr(tarinfo, "tarfile")
    try:
        yield
    finally:
        if tarfile_attr is not _NO_TARFILE_ATTR:
            # mypy doesn't handle seninel objects
            # https://github.com/python/mypy/issues/15788
            tarinfo.tarfile = tarfile_attr  # type: ignore[assignment]


class ReproducibleTarFile(TarFile):
    # Following method modified from Python 3.12
    # https://github.com/python/cpython/blob/09b8b14e05557304ab12870137181685c2dcbe25/Lib/tarfile.py#L1856-L1887
    # Copyright Python Software Foundation, licensed under PSF License Version 2
    # See LICENSE file for full license agreement and notice of copyright
    @classmethod
    def gzopen(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name for reading or writing.
        Appending is not allowed.
        """
        if mode not in ("r", "w", "x"):
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            from gzip import GzipFile
        except ImportError:
            raise CompressionError("gzip module is not available") from None

        try:
            ## repro-tarfile MODIFIED ##
            # Overwrite filename and mtime when initializing GzipFile
            if fileobj is None:
                fileobj = builtins.open(name, mode + "b")
            fileobj = GzipFile("", mode + "b", compresslevel, fileobj, mtime=mtime())
            #########################
        except OSError as e:
            if fileobj is not None and mode == "r":
                raise ReadError("not a gzip file") from e
            raise

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except OSError as e:
            fileobj.close()
            if mode == "r":
                raise ReadError("not a gzip file") from e
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    def addfile(self, tarinfo: TarInfo, fileobj: Optional[IO[bytes]] = None) -> None:
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
        given, it should be a binary file, and tarinfo.size bytes are read
        from it and added to the archive. You can create TarInfo objects
        directly, or by using gettarinfo().
        """
        if tarinfo.isdir():
            mode = 0o40000 | dir_mode()
        else:
            mode = 0o100000 | file_mode()
        # See docstring for _temporarily_delete_tarfile_attr for why we need to do this.
        with _temporarily_delete_tarfile_attr(tarinfo):
            try:
                tarinfo_copy = tarinfo.replace(
                    mtime=mtime(),
                    mode=mode,
                    uid=uid(),
                    gid=gid(),
                    uname=uname(),
                    gname=gname(),
                    deep=True,
                )
            except AttributeError as e:
                # Some older versions of Python don't have replace method
                # Added in: 3.8.17, 3.9.17, 3.10.12, 3.11.4, 3.12
                if "'TarInfo' object has no attribute 'replace'" in str(e):
                    tarinfo_copy = copy.deepcopy(tarinfo)
                    tarinfo_copy.mtime = mtime()
                    tarinfo_copy.mode = mode
                    tarinfo_copy.uid = uid()
                    tarinfo_copy.gid = gid()
                    tarinfo_copy.uname = uname()
                    tarinfo_copy.gname = gname()
                else:
                    raise
        return super().addfile(tarinfo=tarinfo_copy, fileobj=fileobj)


open = ReproducibleTarFile.open
