"""Create Node command."""
from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING
from uuid import UUID

import attr

from orodruin.commands.ports.disconnect_ports import DisconnectPorts
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import ConnectPorts, CreatePort
from .create_node import CreateNode

if TYPE_CHECKING:
    from orodruin.core import (
        Connection,
        Graph,
        GraphLike,
        Node,
        NodeLike,
        Port,
        PortDirection,
        State,
    )


@attr.s
class GroupNodes(Command):
    """Create Node command."""

    state: State = attr.ib()
    graph: GraphLike = attr.ib()
    nodes: List[NodeLike] = attr.ib()

    _nodes: List[Node] = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)
    _created_node: Node = attr.ib(init=False)

    _created_ports: Dict[UUID, Port] = attr.ib(init=False, factory=dict)

    def __attrs_post_init__(self) -> None:
        self._nodes = [self.state.get_node(node) for node in self.nodes]
        self._graph = self.state.get_graph(self.graph)

    def do(self) -> Node:

        self._created_node = CreateNode(self.state, "NewNode", graph=self._graph).do()

        ingoing_connections: Dict[UUID, List[Connection]] = {}

        for node in self._nodes:
            self._graph.unregister_node(node.uuid())
            self._created_node.graph().register_node(node)

            for port in node.ports():
                self._graph.unregister_port(port.uuid())
                self._created_node.graph().register_port(port)
                port.set_graph(self._created_node.graph())

                for connection in list_connections(self._graph, port):
                    if (
                        connection.source().node() in self._nodes
                        and connection.target().node() in self._nodes
                    ):
                        if connection.graph() == self._graph:
                            self._graph.unregister_connection(connection)
                            self._created_node.graph().register_connection(connection)
                    else:
                        if port.direction() is PortDirection.input:
                            source = connection.source()
                            _connections = ingoing_connections.get(source.uuid(), [])
                            _connections.append(connection)
                            ingoing_connections[source.uuid()] = _connections
                        else:
                            target = connection.target()
                            new_port = self._create_or_get_port(
                                port, PortDirection.output
                            )
                            ConnectPorts(
                                self.state,
                                self._graph,
                                new_port,
                                target,
                                force=True,
                            ).do()
                            ConnectPorts(
                                self.state,
                                self._created_node.graph(),
                                port,
                                new_port,
                                force=True,
                            ).do()

        for source_id, connections in ingoing_connections.items():
            source_port = self.state.get_port(source_id)
            new_port = self._create_or_get_port(source_port, PortDirection.input)
            ConnectPorts(
                self.state,
                self._graph,
                source_port,
                new_port,
                force=True,
            ).do()
            for connection in connections:
                DisconnectPorts(
                    self.state, self._graph, connection.source(), connection.target()
                ).do()
                ConnectPorts(
                    self.state,
                    self._created_node.graph(),
                    new_port,
                    connection.target(),
                    force=True,
                ).do()

        return self._created_node

    def undo(self) -> None:
        raise NotImplementedError

    def _create_or_get_port(self, origin_port: Port, direction: PortDirection) -> Port:
        """
        Creates or gets the port on the command's created_node matching the origin_port.

        If the port has a parent, there's a chance it's already been created in
        previous run.
        """
        new_port = self._created_ports.get(origin_port.uuid())
        if new_port:
            return new_port

        top_most_parent = origin_port
        while True:
            parent_port = top_most_parent.parent_port()
            if parent_port is None:
                break
            top_most_parent = parent_port

        new_port = self._create_port(top_most_parent, direction)

        return new_port

    def _create_port(self, origin_port: Port, direction: PortDirection) -> Port:
        """
        Recursively creates a port and all its children on the command's created node
        """
        origin_parent_port = origin_port.parent_port()
        if origin_parent_port:
            parent_port = self._created_ports.get(origin_parent_port.uuid())
        else:
            parent_port = None

        new_port = CreatePort(
            self.state,
            self._created_node,
            origin_port.name(),
            direction,
            origin_port.type(),
            parent_port,
        ).do()

        self._created_ports[origin_port.uuid()] = new_port

        for port in origin_port.child_ports():
            self._create_port(port, direction)

        return new_port
