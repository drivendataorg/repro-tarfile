from gzip import _ReadableFileobj as _GzipReadableFileobj
from gzip import _WritableFileobj as _GzipWritableFileobj
from tarfile import TarFile, _Fileobj
from tarfile import TarInfo as TarInfo
from typing import Literal, Mapping, Self, overload

from _typeshed import ReadableBuffer, StrOrBytesPath, SupportsRead, WriteableBuffer

__all__ = ["open", "ReproducibleTarFile", "TarInfo"]

class ReproducibleTarFile(TarFile):
    # Following type stubs for 'gzopen' copied from Typeshed
    # https://github.com/python/typeshed/blob/494a5d1b98b3522173dd7e0f00f14a32be00456b/stdlib/tarfile.pyi#L380-L415
    # Copyright Python Software Foundation, licensed under Apache License Version 2
    # See LICENSE file for full license agreement and notice of copyright
    @overload
    @classmethod
    def gzopen(
        cls,
        name: StrOrBytesPath | None,
        mode: Literal["r"] = "r",
        fileobj: _GzipReadableFileobj | None = None,
        compresslevel: int = 9,
        *,
        format: int | None = ...,
        tarinfo: type[TarInfo] | None = ...,
        dereference: bool | None = ...,
        ignore_zeros: bool | None = ...,
        encoding: str | None = ...,
        pax_headers: Mapping[str, str] | None = ...,
        debug: int | None = ...,
        errorlevel: int | None = ...,
    ) -> Self: ...
    @overload
    @classmethod
    def gzopen(
        cls,
        name: StrOrBytesPath | None,
        mode: Literal["w", "x"],
        fileobj: _GzipWritableFileobj | None = None,
        compresslevel: int = 9,
        *,
        format: int | None = ...,
        tarinfo: type[TarInfo] | None = ...,
        dereference: bool | None = ...,
        ignore_zeros: bool | None = ...,
        encoding: str | None = ...,
        pax_headers: Mapping[str, str] | None = ...,
        debug: int | None = ...,
        errorlevel: int | None = ...,
    ) -> Self: ...
    def addfile(self, tarinfo: TarInfo, fileobj: SupportsRead[bytes] | None = None) -> None: ...

# Following type stubs for 'open' modified from Typeshed
# https://github.com/python/typeshed/blob/494a5d1b98b3522173dd7e0f00f14a32be00456b/stdlib/tarfile.pyi#L168-L362
# Copyright Python Software Foundation, licensed under Apache License Version 2
# See LICENSE file for full license agreement and notice of copyright
@overload
def open(
    name: StrOrBytesPath | None = None,
    mode: Literal["r", "r:*", "r:", "r:gz", "r:bz2", "r:xz"] = "r",
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    *,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None,
    mode: Literal["x", "x:", "a", "a:", "w", "w:", "w:tar"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    *,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None = None,
    *,
    mode: Literal["x", "x:", "a", "a:", "w", "w:", "w:tar"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None,
    mode: Literal["x:gz", "x:bz2", "w:gz", "w:bz2"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    *,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
    compresslevel: int = 9,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None = None,
    *,
    mode: Literal["x:gz", "x:bz2", "w:gz", "w:bz2"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
    compresslevel: int = 9,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None,
    mode: Literal["x:xz", "w:xz"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    *,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
    preset: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | None = None,
    *,
    mode: Literal["x:xz", "w:xz"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
    preset: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | ReadableBuffer | None = None,
    *,
    mode: Literal["r|*", "r|", "r|gz", "r|bz2", "r|xz"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | WriteableBuffer | None = None,
    *,
    mode: Literal["w|", "w|xz"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
) -> TarFile: ...
@overload
def open(
    name: StrOrBytesPath | WriteableBuffer | None = None,
    *,
    mode: Literal["w|gz", "w|bz2"],
    fileobj: _Fileobj | None = None,
    bufsize: int = 10240,
    format: int | None = ...,
    tarinfo: type[TarInfo] | None = ...,
    dereference: bool | None = ...,
    ignore_zeros: bool | None = ...,
    encoding: str | None = ...,
    errors: str = ...,
    pax_headers: Mapping[str, str] | None = ...,
    debug: int | None = ...,
    errorlevel: int | None = ...,
    compresslevel: int = 9,
) -> TarFile: ...
