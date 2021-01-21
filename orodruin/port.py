"""Orodruin's Port class

A Port is only meant to be attached on a Component
It can be connected to other Ports
"""
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .attribute import (
    BoolAttribute,
    FloatAttribute,
    IntAttribute,
    MatrixAttribute,
    StringAttribute,
)

if TYPE_CHECKING:
    from .component import Component  # pylint: disable = cyclic-import
    from .multiport import MultiPort  # pylint: disable = cyclic-import


class PortType(Enum):
    """Enum representing all the types an attribute can be."""

    int = IntAttribute
    float = FloatAttribute
    bool = BoolAttribute
    string = StringAttribute
    matrix = MatrixAttribute


class PortError(Exception):
    """Generic Port Error."""


class PortAlreadyConnectedError(PortError):
    """Port Already Connected Error."""


class ConnectionOnSameComponenentError(PortError):
    """Both ports about to be connected are on the same component."""


class PortNotConnectedError(PortError):
    """Port Not Connected Error."""


class SetConnectedPortError(PortError):
    """Raised when setting a port that is connected."""


class Port:
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    def __init__(
        self,
        name: str,
        port_type: PortType,
        component: "Component",
    ) -> None:
        self._name: str = name
        self._component: "Component" = component

        self._type = port_type

        self._value: Any = self._type.value.default_value

        self._source: Optional["Port"] = None
        self._targets: List["Port"] = []

    def set(self, value: Any):
        """Set the value of the Port.

        Raises:
            SetConnectedPortError: when called and the port is connected.
        """

        if self._source:
            raise SetConnectedPortError(
                f"Port {self.name} is connected and cannot be set."
            )

        python_type = self._type.value.python_type
        if python_type is not None:
            if not isinstance(value, python_type):
                raise TypeError(
                    f"Can't set port {self._name} to a value of {value}. "
                    f"The port is of type {self._type.name}"
                )

        self._value = value

    def get(self) -> Any:
        """Get the value of the Port.

        When connected, it recursively gets the source's value
        until a non connected port is found.
        """

        if self._source:
            return self._source.get()

        return self._value

    def connect(self, other: Union["Port", "MultiPort"], force: bool = False):
        """Connect this port to another port.

        Raises:
            ConnectionOnSameComponenentError: when trying to connect on another port of
                the same Component
            PortAlreadyConnectedError: when connecting to an already connected port
                and the force argument is False
        """
        if other.component() is self._component:
            raise ConnectionOnSameComponenentError(
                f"{self.name()} and {other.name()} can't be connected because "
                f"they both are on the same component '{self._component.name()}'"
            )

        if self._type.name != other.type().name:
            raise TypeError(
                "Can't connect two ports of different types. "
                f"{self.name()}<{self._type.name}> to "
                f"{other.name()}<{other.type().name}>"
            )

        try:
            # protected-access warning is disabled on the next line
            other = other._receive_connection(self, force)  # pylint: disable = W0212
        except PortAlreadyConnectedError as error:
            raise PortAlreadyConnectedError from error
        else:
            self._targets.append(other)

    def _receive_connection(self, other: Port, force: bool):
        """Connect the other Port to self."""
        if self.source():
            if not force:
                raise PortAlreadyConnectedError(
                    f"port {other.name()} is already connected to "
                    f"{other.source().name()}, "
                    "use `force=True` to connect regardless."
                )

        if self.source() and force:
            other.source().disconnect(other)

        self._source = other
        return self

    def disconnect(self, other: "Port"):
        """Disconnect this port from the other Port."""
        if other not in self._targets:
            return

        self._targets.remove(other)
        other._source = None

    def source(self) -> Optional["Port"]:
        """List of the Ports connected to this Port."""
        return self._source

    def targets(self) -> List["Port"]:
        """List of the Ports this Port connects to."""
        return self._targets

    def component(self) -> "Component":
        """The Component this Port is attached on."""
        return self._component

    def name(self):
        """Name of the Port."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the Port."""
        self._name = name

    def path(self) -> PurePosixPath:
        """The full Path of this Port."""
        return self._component.path().with_suffix(f".{self._name}")

    def type(self) -> PortType:
        """Type of the port."""
        return self._type

    def as_dict(self) -> Dict[str, Any]:
        """Returns a dict representing the Port and its connections."""
        data = {
            "name": self._name,
            "type": self._type.name,
            "source": (
                self._source.path().relative_to(self._component.parent().path())
                if self._source
                else None
            ),
            "targets": [
                c.path().relative_to(self._component.parent().path())
                for c in self._targets
            ],
        }

        return data
