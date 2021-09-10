from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from typing_extensions import Protocol, runtime_checkable

from ..graph_manager import GraphManager
from .types import PortType

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import


class PortDirection(Enum):
    """Directions a port can have."""

    input = "input"
    output = "output"


class SetConnectedPortError(ConnectionError):
    """Raised when setting a port that is connected."""


T = TypeVar("T")  # pylint: disable = invalid-name


@dataclass
class Port(Generic[T]):
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    _name: str
    _direction: PortDirection
    _type: Type[T]
    _component: Component

    _value: T
    _source: Optional[Port[T]] = None
    _targets: List[Port[T]] = field(default_factory=list)

    @classmethod
    def new(
        cls,
        name: str,
        direction: PortDirection,
        port_type: Type[T],
        component: Component,
    ) -> Port[T]:
        """Create a new Port."""

        value: Any
        if issubclass(port_type, PortType):
            value = port_type.new()
        else:
            value = port_type()

        return cls(name, direction, port_type, component, value)

    def component(self) -> Component:
        """The Component this Port is attached on."""
        return self._component

    def type(self) -> Type[T]:
        """Type of the port."""
        return self._type

    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    def source(self) -> Optional[Port[T]]:
        """List of the Ports connected to this Port."""
        return self._source

    def targets(self) -> List[Port[T]]:
        """List of the Ports this Port connects to."""
        return self._targets

    def get(self) -> T:
        """Get the value of the Port.

        When connected, it recursively gets the source's value
        until a non connected port is found.
        """
        if self._source:
            return self._source.get()

        return self._value

    def set(self, value: T) -> None:
        """Set the value of the Port.

        Raises:
            SetConnectedPortError: when called and the port is connected.
        """

        if self._source:
            raise SetConnectedPortError(
                f"Port {self._name} is connected and cannot be set."
            )

        if not isinstance(value, self._type):
            raise TypeError(
                f"Cannot set Port {self._name}[{self._type}] to a value "
                f"of {value}[{type(value)}]."
            )

        self._value = value

    def connect(self, other: Port[T], force: bool = False) -> None:
        """Connect this port to another port."""
        GraphManager.connect_ports(self, other, force)

    def disconnect(self, other: Port[T]) -> None:
        """Disconnect this port from the other Port."""
        GraphManager.disconnect_ports(self, other)

    def external_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections external to the port's component."""
        # the source of an input port can only be outside of the component
        if self._direction is PortDirection.input:
            if self._source:
                return [(self._source, self)]

        # the targets of an input port can only be outside of the component
        elif self._direction is PortDirection.output:
            connections = [(self, t) for t in self._targets]
            return connections

        return []

    def internal_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections internal to the port's component."""
        # the targets of an input port can only be inside of the component
        if self._direction is PortDirection.input:
            connections = [(self, t) for t in self._targets]
            return connections

        # the source of an input port can only be inside of the component
        if self._direction is PortDirection.output:
            if self._source:
                return [(self._source, self)]

        return []

    def name(self) -> str:
        """Name of the port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the port."""
        self._name = name

    def path(self) -> PurePosixPath:
        """The Path of this Port, absolute or relative."""
        path = self._component.path().with_suffix(f".{self.name()}")
        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Port relative to Component."""
        if relative_to is self._component:
            path = PurePosixPath(f".{self.name()}")
        else:
            path = self.path().relative_to(relative_to.path())

        return path
