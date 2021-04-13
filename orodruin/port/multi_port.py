from __future__ import annotations

# pylint: disable = too-many-ancestors
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
    Union,
)

from ..graph_manager import GraphManager
from .port import Port, PortDirection
from .single_port import SinglePort

if TYPE_CHECKING:
    from orodruin.component import Component  # pylint: disable = cyclic-import

T = TypeVar("T")  # pylint: disable = invalid-name


@dataclass
class MultiPort(Generic[T]):
    """Handle over a sequence of ports

    It can be added to a Component like regular Ports but don't own any value directly.
    """

    _name: str
    _direction: PortDirection
    _type: Type[T]
    _component: Component
    size: int

    _ports: List[SinglePort[T]] = field(default_factory=list)

    def __post_init__(self) -> None:
        for _ in range(self.size):
            self.add_port()

    @classmethod
    def new(
        cls,
        name: str,
        direction: PortDirection,
        port_type: Type[T],
        component: Component,
        size: int,
    ) -> MultiPort[T]:
        """Create a new component."""
        return cls(name, direction, port_type, component, size)

    def __getitem__(self, index: int) -> SinglePort[T]:
        return self._ports[index]

    def __setitem__(self, index: int, value: SinglePort[T]) -> None:
        self._ports[index] = value

    def __delitem__(self, index: Union[int, slice]) -> None:
        del self._ports[index]

    def __len__(self) -> int:
        return len(self._ports)

    def insert(self, index: int, value: SinglePort[T]) -> None:
        """Insert a new SinglePort into the MultiPort at a specific index."""
        self._ports.insert(index, value)

    def add_port(self) -> None:
        """Add a Port to this PortCollection."""
        index = len(self._ports)
        port = SinglePort[T].new(
            f"{self._name}[{index}]",
            self._direction,
            self._type,
            self._component,
        )
        self._ports.append(port)

        GraphManager.sync_port_sizes(self)

    def ports(self) -> List[SinglePort[T]]:
        """The SinglePorts of this MultiPort."""
        return self._ports

    def component(self) -> Component:
        """The Component this Port is attached on."""
        return self._component

    def type(self) -> Type[T]:
        """Type of the port."""
        return self._type

    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    def source(self) -> Optional[SinglePort[T]]:
        """Returns the Port connected to the input of this Port"""
        raise NotImplementedError

    def targets(self) -> List[SinglePort[T]]:
        """Returns the Ports connected to the input of this Port"""
        raise NotImplementedError

    def get(self) -> T:
        """Get the value of the all the SinglePort."""
        raise NotImplementedError

    def set(self, value: T) -> None:
        """Raises NotImplementedError."""
        raise NotImplementedError

    def connect(self, other: Port[T], force: bool = False) -> None:
        """Connect this port to another port."""
        raise NotImplementedError

    def disconnect(self, other: Port[T]) -> None:
        """Disconnect this port from the other Port."""
        raise NotImplementedError

    def external_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections external to the port's component."""
        raise NotImplementedError

    def internal_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections internal to the port's component."""
        raise NotImplementedError

    def name(self) -> str:
        """Name of the Port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the Port."""
        self._name = name
        for i, port in enumerate(self.ports()):
            port.set_name(f"{self._name}[{i}]")

    def path(self) -> PurePosixPath:
        """The Path of this Port, absolute or relative."""
        path = self._component.path().with_suffix(f".{self.name()}")
        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Port relative to Component."""
        if relative_to is self._component:
            path = PurePosixPath(f".{self.name}")
        else:
            path = self.path().relative_to(relative_to.path())

        return path
