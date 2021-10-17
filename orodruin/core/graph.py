from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID, uuid4

import attr

from .signal import Signal

if TYPE_CHECKING:
    from .connection import Connection, ConnectionLike
    from .node import Node, NodeLike
    from .port import Port, PortLike
    from .state import State

logger = logging.getLogger(__name__)


@attr.s
class Graph:
    """Orodruin's Graph Class.

    A graph organizes nodes, ports, and connections between them.
    """

    _state: State = attr.ib()
    _parent_node_id: Optional[UUID] = attr.ib(default=None)

    _uuid: UUID = attr.ib(init=False, factory=uuid4)

    _node_ids: List[UUID] = attr.ib(init=False, factory=list)
    _port_ids: List[UUID] = attr.ib(init=False, factory=list)
    _connections_ids: List[UUID] = attr.ib(init=False, factory=list)

    # Signals
    node_registered: Signal[Node] = attr.ib(init=False, factory=Signal)
    node_unregistered: Signal[Node] = attr.ib(init=False, factory=Signal)
    port_registered: Signal[Port] = attr.ib(init=False, factory=Signal)
    port_unregistered: Signal[Port] = attr.ib(init=False, factory=Signal)
    connection_registered: Signal[Connection] = attr.ib(init=False, factory=Signal)
    connection_unregistered: Signal[Connection] = attr.ib(init=False, factory=Signal)

    def state(self) -> State:
        """Return the state that owns this graph."""
        return self._state

    def uuid(self) -> UUID:
        """UUID of this node."""
        return self._uuid

    def nodes(self) -> List[Node]:
        """Return the nodes registered to this graph."""
        nodes = []

        for node_id in self._node_ids:
            node = self._state.get_node(node_id)
            nodes.append(node)

        return nodes

    def ports(self) -> List[Port]:
        """Return the ports registered to this graph."""
        ports = []

        for port_id in self._port_ids:
            port = self._state.get_port(port_id)
            ports.append(port)

        return ports

    def connections(self) -> List[Connection]:
        """Return the connections registered to this graph."""
        connections = []

        for connection_id in self._connections_ids:
            connection = self._state.get_connection(connection_id)
            connections.append(connection)

        return connections

    def parent_node(self) -> Optional[Node]:
        """Return this graph parent node."""
        if self._parent_node_id:
            return self._state.get_node(self._parent_node_id)
        return None

    def register_node(self, node: NodeLike) -> None:
        """Register an existing node to this graph."""
        node = self._state.get_node(node)

        self._node_ids.append(node.uuid())
        node.set_parent_graph(self.uuid())

        logger.debug(
            "Registered node %s to graph %s",
            node.path(),
            self.uuid(),
        )

        self.node_registered.emit(node)

    def unregister_node(self, node: NodeLike) -> None:
        """Remove a registered node from this graph."""
        node = self._state.get_node(node)

        self._node_ids.remove(node.uuid())
        node.set_parent_graph(None)

        logger.debug(
            "Unregistered node %s from graph %s",
            node.path(),
            self.uuid(),
        )

        self.node_unregistered.emit(node)

    def register_port(self, port: PortLike) -> None:
        """Register an existing port to this graph."""
        port = self._state.get_port(port)

        self._port_ids.append(port.uuid())

        logger.debug("Registered port %s to graph %s", port.path(), self.uuid())

        self.port_registered.emit(port)

    def unregister_port(self, port: PortLike) -> None:
        """Remove a registered port from this graph."""
        port = self._state.get_port(port)

        self._port_ids.remove(port.uuid())

        logger.debug("Unregistered port %s from graph %s", port.path(), self.uuid())

        self.port_unregistered.emit(port)

    def register_connection(self, connection: ConnectionLike) -> None:
        """Register an existing connection to this graph."""
        connection = self._state.get_connection(connection)

        self._connections_ids.append(connection.uuid())

        logger.debug(
            "Registered connection %s to graph %s",
            connection.uuid(),
            self.uuid(),
        )

        self.connection_registered.emit(connection)

    def unregister_connection(self, connection: ConnectionLike) -> None:
        """Remove a registered connection from this graph."""
        connection = self._state.get_connection(connection)

        self._connections_ids.remove(connection.uuid())

        logger.debug(
            "Unregistered connection %s from graph %s",
            connection.uuid(),
            self.uuid(),
        )

        self.connection_unregistered.emit(connection)


GraphLike = Union[Graph, UUID]

__all__ = [
    "Graph",
    "GraphLike",
]
