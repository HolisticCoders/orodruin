from pathlib import PurePosixPath

from typing_extensions import Protocol


class PathedObject(Protocol):
    """An Object with a path."""

    @property
    def path(self) -> PurePosixPath:
        """Absolute Path of object."""

    def relative_path(self, relative_to: "PathedObject") -> PurePosixPath:
        """Path of the Object to relative another one."""
