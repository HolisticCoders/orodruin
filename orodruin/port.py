"""Orodruin's Port class

A Port is only meant to be attached on a Component
It can be connected to other Ports
"""
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from orodruin.graph_manager import GraphManager

from .attribute import (
    BoolAttribute,
    FloatAttribute,
    IntAttribute,
    MatrixAttribute,
    StringAttribute,
)

if TYPE_CHECKING:
    from .component import Component  # pylint: disable = cyclic-import


class SetConnectedPortError(ConnectionError):
    """Raised when setting a port that is connected."""


class Port:
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    class Type(Enum):
        """Enum representing all the types an attribute can be."""

        int = IntAttribute
        float = FloatAttribute
        bool = BoolAttribute
        string = StringAttribute
        matrix = MatrixAttribute

    class Direction(Enum):
        """Directions a port can have."""

        input = "input"
        output = "output"

    def __init__(
        self,
        name: str,
        direction: "Port.Direction",
        port_type: "Port.Type",
        component: "Component",
    ) -> None:
        self._name: str = name
        self._component: "Component" = component

        self._type = port_type
        self._direction = direction

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
                f"Port {self.name()} is connected and cannot be set."
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

    def connect(self, other: "Port", force: bool = False):
        """Connect this port to another port."""
        GraphManager.connect_ports(self, other, force)

    def disconnect(self, other: "Port"):
        """Disconnect this port from the other Port."""
        GraphManager.disconnect_ports(self, other)

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

    def path(self, relative_to: Optional["Component"] = None) -> PurePosixPath:
        """The Path of this Port, absolute or relative."""
        path = self._component.path().with_suffix(f".{self._name}")
        if relative_to:
            if relative_to is self._component:
                path = path = PurePosixPath(f".{self._name}")
            else:
                path = path.relative_to(relative_to.path())
        return path

    def type(self) -> "Port.Type":
        """Type of the port."""
        return self._type

    def direction(self) -> "Port.Direction":
        """Direction of the port."""
        return self._direction

    def external_connections(self) -> List[Tuple["Port", "Port"]]:
        """Returns all the connections external to the port's component."""
        # the source of an input port can only be outside of the component
        if self._direction is Port.Direction.input:
            if self._source:
                return [(self._source, self)]

        # the targets of an input port can only be outside of the component
        elif self._direction is Port.Direction.output:
            connections = [(self, t) for t in self._targets]
            return connections

        return []

    def internal_connections(self) -> List[Tuple["Port", "Port"]]:
        """Returns all the connections internal to the port's component."""
        # the targets of an input port can only be inside of the component
        if self._direction is Port.Direction.input:
            connections = [(self, t) for t in self._targets]
            return connections

        # the source of an input port can only be inside of the component
        if self._direction is Port.Direction.output:
            if self._source:
                return [(self._source, self)]

        return []
