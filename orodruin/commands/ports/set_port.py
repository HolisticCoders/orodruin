"""Set Port command."""
from dataclasses import dataclass, field

from orodruin.core import Port, PortType

from ..command import Command


@dataclass
class SetPort(Command[PortType]):
    """Set Port command."""

    port: Port[PortType]
    value: PortType

    _previous_value: PortType = field(init=False)

    def do(self) -> None:
        self._previous_value = self.port.get()
        self.port.set(self.value)

    def undo(self) -> None:
        self.port.set(self._previous_value)
