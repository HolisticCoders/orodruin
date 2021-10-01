"""Create Node command."""
from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID

from orodruin.commands.ports.disconnect_ports import DisconnectPorts
from orodruin.core import Graph, Node
from orodruin.core.connection import Connection
from orodruin.core.graph import GraphLike
from orodruin.core.node import NodeLike
from orodruin.core.port.port import PortDirection
from orodruin.core.state import State
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import ConnectPorts, CreatePort
from .create_node import CreateNode


@dataclass
class GroupNodes(Command):
    """Create Node command."""

    state: State
    graph: GraphLike
    nodes: List[NodeLike]

    _nodes: List[Node] = field(init=False)
    _graph: Graph = field(init=False)
    _created_node: Node = field(init=False)

    def __post_init__(self) -> None:
        self._nodes = [self.state.node_from_nodelike(node) for node in self.nodes]
        self._graph = self.state.graph_from_graphlike(self.graph)

    def do(self) -> Node:

        self._created_node = CreateNode(self.state, "NewNode", graph=self._graph).do()

        ingoing_connections: Dict[UUID, List[Connection]] = {}

        for node in self._nodes:
            self._graph.unregister_node(node.uuid())
            self._created_node.graph().register_node(node)

            for port in node.ports():
                self._graph.unregister_port(port.uuid())
                self._created_node.graph().register_port(port)

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
                            new_port = CreatePort(
                                self.state,
                                self._created_node,
                                port.name(),
                                PortDirection.output,
                                port.type(),
                            ).do()
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
            source_port = self.state.port_from_portlike(source_id)
            new_port = CreatePort(
                self.state,
                self._created_node,
                source_port.name(),
                PortDirection.input,
                source_port.type(),
            ).do()
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
