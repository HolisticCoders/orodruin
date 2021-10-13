"""Rename Node command."""
from dataclasses import dataclass, field

from orodruin.core.port.port import Port, PortLike
from orodruin.core.state import State
from orodruin.core.utils import get_unique_port_name

from ..command import Command


@dataclass
class RenamePort(Command):
    """Rename Node command."""

    state: State
    port: PortLike
    name: str

    _port: Port = field(init=False)
    _old_name: str = field(init=False)
    _new_name: str = field(init=False)

    def __post_init__(self) -> None:
        self._port = self.state.get_port(self.port)

    def do(self) -> str:
        self._old_name = self._port.name()

        if self.name == self._old_name:
            # Don't rename the port to avoid emiting the name_changed signal
            self._new_name = self._old_name
            return self._old_name

        parent_node = self._port.node()

        self._new_name = get_unique_port_name(parent_node, self.name)

        self._port.set_name(self._new_name)

        return self._new_name

    def undo(self) -> None:
        self._port.set_name(self._old_name)

    def redo(self) -> None:
        self._port.set_name(self._new_name)
