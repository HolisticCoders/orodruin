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
class Node:
    """Orodruin's Node Class.

    A node can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Nodes as a subgraph
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
    name_changed: Signal[str] = field(init=False, default_factory=Signal)
    port_registered: Signal[Port] = field(init=False, default_factory=Signal)
    port_unregistered: Signal[Port] = field(init=False, default_factory=Signal)

    def post_node_created(self) -> None:
        """Method called after the state has created and registered the node."""

        # The graph has to be created after the `State.node_created` signal is emitted
        # or `Graph._parent_node_id` will point to a node not yet registered.
        self._graph_id = self._state.create_graph(self.uuid()).uuid()

    def state(self) -> State:
        """Return the state that owns this node."""
        return self._state

    def uuid(self) -> UUID:
        """UUID of this node."""
        return self._uuid

    def name(self) -> str:
        """Name of the node."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of this node."""
        old_name = self._name
        self._name = name

        logger.debug("Renamed node %s to %s.", old_name, name)

        self.name_changed.emit(name)

    def type(self) -> str:
        """Type of this node."""
        return self._type

    def set_type(self, value: str) -> None:
        """Type of this Node."""
        self._type = value

    def library(self) -> Optional[Library]:
        """Return the library declaring this node."""
        return self._library

    def set_library(self, library: Library) -> None:
        """Set the library declaring this node."""
        self._library = library

    def path(self) -> PurePosixPath:
        """Absolute Path of this node."""
        parent = self.parent_node()
        if parent:
            path = parent.path() / self.name()
        else:
            path = PurePosixPath(f"/{self.name()}")

        return path

    def relative_path(self, relative_to: Node) -> PurePosixPath:
        """Path of the Node relative to another one."""
        return self.path().relative_to(relative_to.path())

    def ports(self) -> List[Port]:
        """Return the ports registered to this node."""
        ports = []

        for port_id in self._port_ids:
            port = self._state.get_port(port_id)
            ports.append(port)

        return ports

    def parent_graph(self) -> Optional[Graph]:
        """Parent graph of the node."""
        if self._parent_graph_id:
            return self._state.get_graph(self._parent_graph_id)
        return None

    def set_parent_graph(self, graph: Optional[GraphLike]) -> None:
        """Set the parent graph of the node."""
        if graph:
            graph = self.state().get_graph(graph)
            self._parent_graph_id = graph.uuid()
        else:
            self._parent_graph_id = None

    def graph(self) -> Graph:
        """Graph containing child nodes."""
        return self._state.get_graph(self._graph_id)

    def parent_node(self) -> Optional[Node]:
        """Parent node."""
        parent_graph = self.parent_graph()
        if not parent_graph:
            return None
        return parent_graph.parent_node()

    def port(self, name: str) -> Port:
        """Get a Port of this node from the its name."""
        for port in self.ports():
            if port.name() == name:
                return port

        raise NameError(f"Node {self.name()} has no port named {name}")

    def register_port(self, port: PortLike) -> None:
        """Register an existing port to this node."""
        port = self._state.get_port(port)

        self._port_ids.append(port.uuid())

        logger.debug("Registered port %s to node %s", port.path(), self.path())

        self.port_registered.emit(port)

    def unregister_port(self, port: PortLike) -> None:
        """Remove a registered port from this node."""
        port = self._state.get_port(port)

        self._port_ids.remove(port.uuid())

        logger.debug("Unregistered port %s from node %s", port.path(), self.path())

        self.port_unregistered.emit(port)


NodeLike = Union[Node, UUID]

__all__ = [
    "Node",
    "NodeLike",
]
