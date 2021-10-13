from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID, uuid4

from orodruin.core.graph import Graph
from orodruin.core.signal import Signal

from .types import PortType

if TYPE_CHECKING:
    from ..node import Node  # pylint: disable = cyclic-import
    from ..state import State

logger = logging.getLogger(__name__)


class PortDirection(Enum):
    """Directions a port can have."""

    input = "input"
    output = "output"


@dataclass
class Port(Generic[PortType]):
    """Orodruin's Port class

    A Port is only meant to be attached on a Node
    It can be connected to other Ports and hold a value
    """

    _state: State
    _graph_id: UUID
    _node_id: UUID

    _name: str
    _direction: PortDirection
    _type: Type[PortType]

    _value: PortType = field(init=False)

    _parent_port_id: Optional[UUID] = field(init=False, default=None)
    _child_port_ids: List[UUID] = field(init=False, default_factory=list)

    _uuid: UUID = field(default_factory=uuid4)

    name_changed: Signal[str] = field(init=False, default_factory=Signal)

    def __post_init__(self) -> None:
        self._value = self._type()

    def state(self) -> State:
        """Return the state that owns this port."""
        return self._state

    def graph(self) -> Graph:
        """Return the graph that this port exists in."""
        return self._state.get_graph(self._graph_id)

    def node(self) -> Node:
        """The Node this Port is attached on."""
        return self._state.get_node(self._node_id)

    def uuid(self) -> UUID:
        """UUID of this port."""
        return self._uuid

    def name(self) -> str:
        """Name of the port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of this port."""
        old_name = self._name
        self._name = name

        logger.debug("Renamed port %s to %s.", old_name, name)

        self.name_changed.emit(name)

    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    def type(self) -> Type[PortType]:
        """Type of the port."""
        return self._type

    def get(self) -> PortType:
        """Get the value of the Port.

        When connected, it recursively gets the source's value
        until a non connected port is found.
        """
        return self._value

    def set(self, value: PortType) -> None:
        """Set the value of the Port.

        Raises:
            SetConnectedPortError: when called and the port is connected.
        """
        try:
            self._type(value)  # type: ignore[arg-type]
        except Exception as error:
            raise TypeError(
                f"Cannot set Port {self._name}[{self._type.__name__}] to a value "
                f"of {value}."
            ) from error

        self._value = value

    def parent_port(self) -> Optional[Port]:
        """Parent port of the port."""
        if self._parent_port_id:
            return self._state.get_port(self._parent_port_id)
        return None

    def set_parent_port(self, port: Port) -> None:
        """Set the parent port of the port."""
        self._parent_port_id = port.uuid()

    def child_ports(self) -> List[Port]:
        """Children of the port."""
        return [self._state.get_port(port) for port in self._child_port_ids]

    def add_child_port(self, port: Port) -> None:
        """Add a child port to the port."""
        self._child_port_ids.append(port.uuid())

    def path(self) -> PurePosixPath:
        """The absolute path of this Port."""
        return self.node().path().with_suffix(f".{self.name()}")

    def relative_path(self, relative_to: Node) -> PurePosixPath:
        """The relative path of the port to the node."""
        if relative_to is self.node():
            path = PurePosixPath(f".{self.name()}")
        else:
            path = self.path().relative_to(relative_to.path())

        return path


PortLike = Union[Port[PortType], UUID]

__all__ = [
    "Port",
    "PortType",
    "PortLike",
]
