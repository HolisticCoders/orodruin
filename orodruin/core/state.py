from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type
from uuid import UUID

from orodruin.core.library import Library
from orodruin.core.port.port import PortDirection
from orodruin.core.signal import Signal

from .node import Node, NodeLike
from .connection import Connection, ConnectionLike
from .graph import Graph, GraphLike
from .port import Port, PortLike, PortType

logger = logging.getLogger(__name__)


@dataclass
class State:
    """Orodruin's State class.

    This is the object that "owns" all the Graphs, Nodes, Ports and Connections.
    Nothing else than the state should hold direct references to any of these objects.
    Instead, the UUIDs should be stored and objects accessed when needed
    with the State.object_from_objectlike methods.
    """

    _root_graph: Graph = field(init=False)

    _graphs: Dict[UUID, Graph] = field(init=False, default_factory=dict)
    _nodes: Dict[UUID, Node] = field(init=False, default_factory=dict)
    _ports: Dict[UUID, Port] = field(init=False, default_factory=dict)
    _connections: Dict[UUID, Connection] = field(init=False, default_factory=dict)

    # Signals
    graph_created: Signal[Graph] = field(default_factory=Signal)
    graph_deleted: Signal[UUID] = field(default_factory=Signal)
    node_created: Signal[Node] = field(default_factory=Signal)
    node_deleted: Signal[UUID] = field(default_factory=Signal)
    port_created: Signal[Port] = field(default_factory=Signal)
    port_deleted: Signal[UUID] = field(default_factory=Signal)
    connection_created: Signal[Connection] = field(default_factory=Signal)
    connection_deleted: Signal[UUID] = field(default_factory=Signal)

    def __post_init__(self) -> None:
        self._root_graph = self.create_graph()

    def root_graph(self) -> Graph:
        "return the state's root graph"
        return self._root_graph

    def graph_from_graphlike(self, graph: GraphLike) -> Graph:
        """Return a Graph from a GraphLike object.

        Raises:
            TypeError: When the graph is not a valid GraphLike object.
        """
        if isinstance(graph, Graph):
            pass
        elif isinstance(graph, UUID):
            graph = self._graphs[graph]
        else:
            raise TypeError(
                f"{type(graph)} is not a valid GraphLike type. "
                "Should be Union[Graph, UUID]"
            )

        return graph

    def node_from_nodelike(self, node: NodeLike) -> Node:
        """Return a Node from a NodeLike object.

        Raises:
            TypeError: When the node is not a valid NodeLike object.
        """
        if isinstance(node, Node):
            pass
        elif isinstance(node, UUID):
            node = self._nodes[node]
        else:
            raise TypeError(
                f"{type(node)} is not a valid NodeLike type. "
                "Should be Union[Node, UUID]"
            )

        return node

    def port_from_portlike(self, port: PortLike) -> Port:
        """Return a Port from a PortLike object.

        Raises:
            TypeError: When the port is not a valid PortLike object.
        """
        if isinstance(port, Port):
            pass
        elif isinstance(port, UUID):
            port = self._ports[port]
        else:
            raise TypeError(
                f"{type(port)} is not a valid PortLike type. "
                "Should be Union[Port, UUID]"
            )

        return port

    def connection_from_connectionlike(self, connection: ConnectionLike) -> Connection:
        """Return a Connection from a ConnectionLike object.

        Raises:
            TypeError: When the connection is not a valid ConnectionLike object.
        """
        if isinstance(connection, Connection):
            pass
        elif isinstance(connection, UUID):
            connection = self._connections[connection]
        else:
            raise TypeError(
                f"{type(connection)} is not a valid ConnectionLike type. "
                "Should be Union[Connection, UUID]"
            )

        return connection

    def graphs(self) -> List[Graph]:
        """Return a list of the registered graphs."""
        return list(self._graphs.values())

    def nodes(self) -> List[Node]:
        """Return a list of the registered nodes."""
        return list(self._nodes.values())

    def ports(self) -> List[Port]:
        """Return a list of the registered ports."""
        return list(self._ports.values())

    def connections(self) -> List[Connection]:
        """Return a list of the registered connections."""
        return list(self._connections.values())

    def create_graph(self, parent_node: Optional[NodeLike] = None) -> Graph:
        """Create graph and register it to the state."""

        if isinstance(parent_node, Node):
            parent_node = parent_node.uuid()

        graph = Graph(self, parent_node)
        self._graphs[graph.uuid()] = graph
        self.graph_created.emit(graph)

        logger.debug("Created graph %s.", graph.uuid())

        return graph

    def delete_graph(self, graph: GraphLike) -> None:
        """Delete a graph and unregister it from the state."""

        graph = self.graph_from_graphlike(graph)

        del self._graphs[graph.uuid()]

        self.graph_deleted.emit(graph.uuid())

        logger.debug("Deleted graph %s.", graph.uuid())

    def create_node(
        self,
        name: str,
        node_type: Optional[str] = None,
        library: Optional[Library] = None,
        parent_graph_id: Optional[UUID] = None,
    ) -> Node:
        """Create graph and register it to the state."""
        if not parent_graph_id:
            parent_graph_id = self.root_graph().uuid()

        node = Node(
            _state=self,
            _parent_graph_id=parent_graph_id,
            _name=name,
            _library=library,
        )
        if node_type:
            node.set_type(node_type)

        self._nodes[node.uuid()] = node

        self.node_created.emit(node)

        logger.debug("Created node %s.", node.path())

        return node

    def delete_node(self, node: NodeLike) -> None:
        """Delete a node and unregister it from the state."""

        node = self.node_from_nodelike(node)

        del self._nodes[node.uuid()]

        self.node_deleted.emit(node.uuid())

        logger.debug("Deleted node %s.", node.path())

    def create_port(
        self,
        name: str,
        direction: PortDirection,
        port_type: Type[PortType],
        node: NodeLike,
    ) -> Port[PortType]:
        """Create a port and register it to the state."""

        node = self.node_from_nodelike(node)

        graph = node.parent_graph()
        port = Port(
            self,
            graph.uuid(),
            node.uuid(),
            name,
            direction,
            port_type,
        )

        self._ports[port.uuid()] = port

        self.port_created.emit(port)

        logger.debug("Created port %s.", port.path())

        return port

    def delete_port(self, port: PortLike) -> None:
        """Delete a port and unregister it from the state."""

        port = self.port_from_portlike(port)

        del self._ports[port.uuid()]

        self.port_deleted.emit(port.uuid())

        logger.debug("Deleted port %s from the state.", port.path())

    def create_connection(
        self,
        source: PortLike,
        target: PortLike,
    ) -> Connection:
        """Create a connection and register it to the state."""

        source = self.port_from_portlike(source)
        target = self.port_from_portlike(target)

        connection = Connection(self, source.uuid(), target.uuid())
        self._connections[connection.uuid()] = connection
        self.connection_created.emit(connection)

        logger.debug("Created connection %s.", connection.uuid())

        return connection

    def delete_connection(self, connection: ConnectionLike) -> None:
        """Delete a connection and unregister it from the state."""

        connection = self.connection_from_connectionlike(connection)

        del self._connections[connection.uuid()]

        self.connection_deleted.emit(connection.uuid())

        logger.debug("Deleted connection %s.", connection.uuid())
