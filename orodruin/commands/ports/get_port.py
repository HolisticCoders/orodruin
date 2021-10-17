"""Get Port command."""
import attr

from orodruin.core import Port, PortType

from ..command import Command


@attr.s
class GetPort(Command[PortType]):
    """Get Port command."""

    port: Port[PortType] = attr.ib()

    def do(self) -> PortType:
        return self.port.get()

    def undo(self) -> None:
        """Command is not undoable."""
