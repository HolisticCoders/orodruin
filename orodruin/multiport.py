"""Multi Port is a handle on a sequence of ports."""
from collections.abc import Sequence
from typing import TYPE_CHECKING, List

from .port import Port, PortType

if TYPE_CHECKING:
    from orodruin.component import Component  # pylint: disable = cyclic-import


class MultiPort(Sequence):
    """Handle over a sequence of ports

    It can be added to a Component like regular Ports but don't own any value directly.
    """

    def __init__(
        self,
        name: str,
        port_type: PortType,
        component: "Component",
    ) -> None:
        super().__init__()

        self._name: str = name
        self._component: "Component" = component

        self._type = port_type

        self._ports: List["Port"] = []

    def __getitem__(self, index):
        return self._ports[index]

    def __len__(self, *args, **kwargs):
        return len(self._ports)

    def add_port(self):
        """Add a Port to this MultiPort."""
        index = len(self._ports)
        port = Port(f"{self._name}[{index}]", self._type, self._component)
        self._ports.append(port)

    def name(self):
        """Name of the Port."""
        return self._name

    def set_name(self, value: str):
        """Set the name of the MultiPort.

        This will rename all the sub-Ports accordingly.
        """
        self._name = value

        for index, port in enumerate(self._ports):
            port.set_name(f"{self._name}[{index}]")

    def type(self):
        """Type of the port."""
        return self._type

    def component(self):
        """The Component this Port is attached on."""
        return self._component

    def _receive_connection(self, other: Port, force: bool):
        """Create a new sub port and connect the other Port to it."""
        self.add_port()
        port = self[-1]
        port._receive_connection(other, force)  # pylint: disable= protected-access
        return port
