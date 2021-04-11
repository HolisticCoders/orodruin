from __future__ import annotations

# pylint: disable = too-many-ancestors
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar, Union

from ..graph_manager import GraphManager
from .port import PortDirection
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
            f"{self.name}[{index}]",
            self.direction,
            self.type,
            self._component,
        )
        self._ports.append(port)

        GraphManager.sync_port_sizes(self)

    @property
    def name(self) -> str:
        """Name of the Port."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        for i, port in enumerate(self.ports):
            port.name = f"{self.name}[{i}]"

    @property
    def ports(self) -> List[SinglePort[T]]:
        """The SinglePorts of this MultiPort."""
        return self._ports

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
        """Returns the Port connected to the input of this Port"""
        raise NotImplementedError

    @property
    def targets(self) -> List[SinglePort[T]]:
        """Returns the Ports connected to the input of this Port"""
        raise NotImplementedError

    def get(self) -> T:
        """Get the value of the all the SinglePort."""
        raise NotImplementedError

    def set(self, _: List[T]) -> None:
        """Raises NotImplementedError."""
        # TODO: implement this.
        # This should make sure the length of the MultiPort is compatible with
        # the length of the list.

        raise NotImplementedError
