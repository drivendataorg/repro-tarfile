import contextlib
import datetime
import os
import tarfile
from typing import IO, Optional

__version__ = "0.1.0"


def date_time() -> int:
    """Returns date_time value used to force overwrite on all TarInfo objects. Defaults to
    315550800 (corresponding to 1980-01-01 00:00:00 UTC). You can set this with the environment
    variable SOURCE_DATE_EPOCH as an integer value representing seconds since Epoch.
    """
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH", None)
    if source_date_epoch is not None:
        return int(source_date_epoch)
    return int(datetime.datetime(1980, 1, 1, 0, 0, 0).timestamp())


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
def _temporarily_delete_tarfile_attr(tarinfo: tarfile.TarInfo):
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
            tarinfo.tarfile = tarfile_attr


class ReproducibleTarFile(tarfile.TarFile):
    def addfile(self, tarinfo: tarfile.TarInfo, fileobj: Optional[IO[bytes]] = None) -> None:
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
            tarinfo_copy = tarinfo.replace(
                mtime=date_time(),
                mode=mode,
                uid=uid(),
                gid=gid(),
                uname=uname(),
                gname=gname(),
                deep=True,
            )
        return super().addfile(tarinfo=tarinfo_copy, fileobj=fileobj)


open = ReproducibleTarFile.open
