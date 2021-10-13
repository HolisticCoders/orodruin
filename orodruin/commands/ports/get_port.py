"""Get Port command."""
from dataclasses import dataclass

from orodruin.core import Port, PortType

from ..command import Command


@dataclass
class GetPort(Command[PortType]):
    """Get Port command."""

    port: Port[PortType]

    def do(self) -> PortType:
        return self.port.get()

    def undo(self) -> None:
        """Command is not undoable."""
