# pylint: disable = too-many-ancestors
"""Multi Port is a handle on a sequence of ports."""
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, List

from .graph_manager import GraphManager
from .port import Port

if TYPE_CHECKING:
    from orodruin.component import Component  # pylint: disable = cyclic-import


class PortCollection(MutableSequence):
    """Handle over a sequence of ports

    It can be added to a Component like regular Ports but don't own any value directly.
    """

    def __init__(
        self,
        name: str,
        direction: Port.Direction,
        port_type: Port.Type,
        component: "Component",
        size: int = 0,
    ) -> None:
        super().__init__()

        self._name: str = name
        self._component: "Component" = component

        self._type = port_type
        self._direction = direction

        self._ports: List["Port"] = []

        for _ in range(size):
            self.add_port()

    def __getitem__(self, index: int):
        return self._ports[index]

    def __setitem__(self, index: int, value: "Port"):
        self._ports[index] = value

    def __delitem__(self, index: int):
        del self._ports[index]

    def __len__(self):
        return len(self._ports)

    def insert(self, index: int, value: "Port"):
        self._ports.insert(index, value)

    def add_port(self):
        """Add a Port to this PortCollection."""
        index = len(self._ports)
        port = Port(
            f"{self._name}[{index}]",
            self._direction,
            self._type,
            self._component,
        )
        self.append(port)

        GraphManager.sync_port_sizes(self)

    def name(self):
        """Name of the Port."""
        return self._name

    def type(self):
        """Type of the port."""
        return self._type

    def direction(self) -> Port.Direction:
        """Direction of the port."""
        return self._direction

    def component(self):
        """The Component this Port is attached on."""
        return self._component

    def ports(self):
        """The ports owned by this PortCollection."""
        return self._ports
