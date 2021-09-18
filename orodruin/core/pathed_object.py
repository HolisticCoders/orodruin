from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .component import Component


@runtime_checkable
class PathedObject(Protocol):
    """An Object with a path."""

    def name(self) -> str:
        """Name of the object."""

    def set_name(self, name: str) -> None:
        """Set the name of the object."""

    def path(self) -> PurePosixPath:
        """Absolute Path of object."""

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Object to relative another one."""
