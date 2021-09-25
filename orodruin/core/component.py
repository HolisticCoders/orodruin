from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID, uuid4

from .graph import Graph, GraphLike
from .signal import Signal

if TYPE_CHECKING:
    from .library import Library  # pylint: disable = cyclic-import
    from .port import Port, PortLike
    from .state import State

logger = logging.getLogger(__name__)


@dataclass
class Component:
    """Orodruin's Component Class.

    A component can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Components as a subgraph
    """

    _state: State
    _parent_graph_id: Optional[UUID]

    _name: str
    _type: str = field(default_factory=lambda: str(uuid4()))
    _library: Optional[Library] = None

    _uuid: UUID = field(default_factory=uuid4)

    _graph_id: UUID = field(init=False)
    _port_ids: List[UUID] = field(default_factory=list)

    # Signals
    name_changed: Signal[str] = field(default_factory=Signal)
    port_registered: Signal[Port] = field(default_factory=Signal)
    port_unregistered: Signal[Port] = field(default_factory=Signal)

    def __post_init__(self) -> None:
        self._graph_id = self._state.create_graph(self.uuid()).uuid()

    def state(self) -> State:
        """Return the state that owns this component."""
        return self._state

    def uuid(self) -> UUID:
        """UUID of this component."""
        return self._uuid

    def name(self) -> str:
        """Name of the component."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of this component."""
        self._name = name
        self.name_changed.emit(name)

    def type(self) -> str:
        """Type of this component."""
        return self._type

    def set_type(self, value: str) -> None:
        """Type of this Component."""
        self._type = value

    def library(self) -> Optional[Library]:
        """Return the library declaring this component."""
        return self._library

    def set_library(self, library: Library) -> None:
        """Set the library declaring this component."""
        self._library = library

    def path(self) -> PurePosixPath:
        """Absolute Path of this component."""
        parent = self.parent_component()
        if parent:
            path = parent.path() / self.name()
        else:
            path = PurePosixPath(f"/{self.name()}")

        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Component relative to another one."""
        return self.path().relative_to(relative_to.path())

    def ports(self) -> List[Port]:
        """Return the ports registered to this component."""
        ports = []

        for port_id in self._port_ids:
            port = self._state.port_from_portlike(port_id)
            ports.append(port)

        return ports

    def parent_graph(self) -> Optional[Graph]:
        """Parent graph of the component."""
        if self._parent_graph_id:
            return self._state.graph_from_graphlike(self._parent_graph_id)
        return None

    def set_parent_graph(self, graph: Optional[GraphLike]) -> None:
        """Set the parent graph of the component."""
        if graph:
            graph = self.state().graph_from_graphlike(graph)
            self._parent_graph_id = graph.uuid()
        else:
            self._parent_graph_id = None

    def graph(self) -> Graph:
        """Graph containing child components."""
        return self._state.graph_from_graphlike(self._graph_id)

    def parent_component(self) -> Optional[Component]:
        """Parent component."""
        parent_graph = self.parent_graph()
        if not parent_graph:
            return None
        return parent_graph.parent_component()

    def port(self, name: str) -> Port:
        """Get a Port of this node from the its name."""
        for port in self.ports():
            if port.name() == name:
                return port

        raise NameError(f"Component {self.name()} has no port named {name}")

    def register_port(self, port: PortLike) -> None:
        """Register an existing port to this component."""
        port = self._state.port_from_portlike(port)

        self._port_ids.append(port.uuid())
        self.port_registered.emit(port)

        logger.debug("Registered port %s to component %s", port.path(), self.path())

    def unregister_port(self, port: PortLike) -> None:
        """Remove a registered port from this component."""
        port = self._state.port_from_portlike(port)

        self._port_ids.remove(port.uuid())
        self.port_unregistered.emit(port)

        logger.debug("Unregistered port %s from component %s", port.path(), self.path())


ComponentLike = Union[Component, UUID]

__all__ = [
    "Component",
    "ComponentLike",
]
