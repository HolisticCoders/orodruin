"""Get Port command."""
from dataclasses import dataclass
from typing import TypeVar

from orodruin.core import Port

from ..command import Command

T = TypeVar("T")


@dataclass
class GetPort(Command[T]):
    """Get Port command."""

    port: Port[T]

    def do(self) -> T:
        return self.port.get()

    def undo(self) -> None:
        """Command is not undoable."""
