"""Orodruin's Port class

A Port is only meant to be attached on a Component
It can be connected to other Ports
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class PortError(Exception):
    """Generic Port Error."""


class PortAlreadyConnected(PortError):
    """Port Already Connected Error."""


class PortNotConnected(PortError):
    """Port Not Connected Error."""


class PortSide(Enum):
    """Side of a Port on a Component."""

    input = 1
    output = 2


class Port:
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports
    """

    def __init__(self, name: str, uuid: Optional[UUID] = None) -> None:
        self._name: str = name
        self._connections: List[Port] = []

        # TODO: implement port types
        # self._value: Any = None

        self._uuid: UUID
        if uuid:
            self._uuid = uuid
        else:
            self._uuid = uuid4()

    def connect(self, other: "Port"):
        """Connect this port to another port."""
        if other in self._connections:
            raise PortAlreadyConnected(
                f"port {self.name()} is already connected to {other.name()}"
            )
        self._connections.append(other)
        other._connections.append(self)

    def disconnect(self, other: "Port"):
        """Disconnect this port from the other Port."""
        if other not in self._connections:
            raise PortNotConnected(
                f"port {self.name()} is not connected to {other.name()}"
            )
        self._connections.remove(other)
        other._connections.remove(self)

    def connections(self):
        """The connected Ports of this Port."""
        return self._connections

    def name(self):
        """Name of the Port."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the Port."""
        self._name = name

    def uuid(self):
        """UUID of the Component"""
        return self._uuid

    def as_dict(self) -> Dict[str, Any]:
        """Returns a dict representing the Port and its connections."""
        data = {
            "name": self._name,
            "uuid": self._uuid,
            "connections": [c.uuid() for c in self._connections],
        }

        return data
