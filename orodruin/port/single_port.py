from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from ..graph_manager import GraphManager
from .port import Port, PortDirection
from .types import PortType

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import


class SetConnectedPortError(ConnectionError):
    """Raised when setting a port that is connected."""


T = TypeVar("T")  # pylint: disable = invalid-name


@dataclass
class SinglePort(Generic[T]):
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    name: str
    _direction: PortDirection
    _type: Type[T]
    _component: Component

    _value: T
    _source: Optional[SinglePort[T]] = None
    _targets: List[SinglePort[T]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self._value is None:
            self._value = self.type()

    @classmethod
    def new(
        cls,
        name: str,
        direction: PortDirection,
        port_type: Type[T],
        component: Component,
    ) -> SinglePort[T]:
        """Create a new SinglePort."""

        if isinstance(port_type, PortType):
            value = port_type.new()
        else:
            value = port_type()

        return cls(name, direction, port_type, component, value)

    @property
    def component(self) -> Component:
        """The Component this Port is attached on."""
        return self._component

    @property
    def type(self) -> Type[T]:
        """Type of the port."""
        return self._type

    @property
    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    @property
    def source(self) -> Optional[SinglePort[T]]:
        """List of the Ports connected to this Port."""
        return self._source

    @property
    def targets(self) -> List[SinglePort[T]]:
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
                f"Port {self.name} is connected and cannot be set."
            )

        if not isinstance(value, self.type):
            raise TypeError(
                f"Cannot set Port {self.name}[{self.type}] to a value "
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
        if self.direction is PortDirection.input:
            if self.source:
                return [(self.source, self)]

        # the targets of an input port can only be outside of the component
        elif self._direction is PortDirection.output:
            connections = [(self, t) for t in self.targets]
            return connections

        return []

    def internal_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections internal to the port's component."""
        # the targets of an input port can only be inside of the component
        if self.direction is PortDirection.input:
            connections = [(self, t) for t in self.targets]
            return connections

        # the source of an input port can only be inside of the component
        if self.direction is PortDirection.output:
            if self.source:
                return [(self.source, self)]

        return []

    @property
    def path(self) -> PurePosixPath:
        """The Path of this Port, absolute or relative."""
        path = self._component.path.with_suffix(f".{self.name}")
        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Port relative to Component."""
        if relative_to is self._component:
            path = PurePosixPath(f".{self.name}")
        else:
            path = self.path.relative_to(relative_to.path)

        return path
