"""Set Port command."""
import attr

from orodruin.core import Port, PortType

from ..command import Command


@attr.s
class SetPort(Command[PortType]):
    """Set Port command."""

    port: Port[PortType] = attr.ib()
    value: PortType = attr.ib()

    _previous_value: PortType = attr.ib(init=False)

    def do(self) -> None:
        self._previous_value = self.port.get()
        self.port.set(self.value)

    def undo(self) -> None:
        self.port.set(self._previous_value)
