"""Orodruin's Port class

A Port is only meant to be attached on a Component
It can be connected to other Ports
"""
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List

from pathlib import PurePosixPath

if TYPE_CHECKING:
    from orodruin.component import Component


class PortError(Exception):
    """Generic Port Error."""


class PortAlreadyConnectedError(PortError):
    """Port Already Connected Error."""


class ConnectionOnSameComponenentError(PortError):
    """Both ports about to be connected are on the same component."""


class PortNotConnectedError(PortError):
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

    def __init__(self, name: str, component: "Component") -> None:
        self._name: str = name
        self._connections: List["Port"] = []
        self._component: "Component" = component

        # TODO: implement port types
        # self._value: Any = None

    def connect(self, other: "Port"):
        """Connect this port to another port."""
        if other.component() is self._component:
            raise ConnectionOnSameComponenentError(
                f"{self.name()} and {other.name()} can't be connected because they both are on the same component '{self._component.name()}'"
            )
        if other in self._connections:
            raise PortAlreadyConnectedError(
                f"port {self.name()} is already connected to {other.name()}"
            )
        self._connections.append(other)
        other._connections.append(self)

    def disconnect(self, other: "Port"):
        """Disconnect this port from the other Port."""
        if other not in self._connections:
            raise PortNotConnectedError(
                f"port {self.name()} is not connected to {other.name()}"
            )
        self._connections.remove(other)
        other._connections.remove(self)

    def connections(self) -> List["Port"]:
        """The connected Ports of this Port."""
        return self._connections

    def component(self) -> "Component":
        return self._component

    def name(self):
        """Name of the Port."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the Port."""
        self._name = name

    def path(self) -> PurePosixPath:
        return self._component.path() / f".{self._name}"

    def as_dict(self) -> Dict[str, Any]:
        """Returns a dict representing the Port and its connections."""
        data = {
            "name": self._name,
            "connections": [
                c.path().relative_to(self._component.parent().path())
                for c in self._connections
            ],
        }

        return data
