from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

import attr

from orodruin.core.deserializer import ExternalDeserializer, Deserializer
from orodruin.core.library import Library
from orodruin.core.port.port import PortDirection
from orodruin.core.serializer import ExternalSerializer, Serializer
from orodruin.core.signal import Signal

from .connection import Connection, ConnectionLike
from .graph import Graph, GraphLike
from .node import Node, NodeLike
from .port import Port, PortLike, PortType

logger = logging.getLogger(__name__)


@attr.s
class State:
    """Orodruin's State class.

    This is the object that "owns" all the Graphs, Nodes, Ports and Connections.
    Nothing else than the state should hold direct references to any of these objects.
    Instead, the UUIDs should be stored and objects accessed when needed
    with the State.object_from_objectlike methods.
    """

    _root_graph: Graph = attr.ib(init=False)
    _root_serializer: Serializer = attr.ib(init=False)
    _root_deserializer: Deserializer = attr.ib(init=False)

    _graphs: Dict[UUID, Graph] = attr.ib(init=False, factory=dict)
    _nodes: Dict[UUID, Node] = attr.ib(init=False, factory=dict)
    _ports: Dict[UUID, Port] = attr.ib(init=False, factory=dict)
    _connections: Dict[UUID, Connection] = attr.ib(init=False, factory=dict)
    _serializers: List[ExternalSerializer] = attr.ib(init=False, factory=list)
    _deserializers: List[ExternalDeserializer] = attr.ib(init=False, factory=list)

    # Signals
    graph_created: Signal[Graph] = attr.ib(init=False, factory=Signal)
    graph_deleted: Signal[UUID] = attr.ib(init=False, factory=Signal)
    node_created: Signal[Node] = attr.ib(init=False, factory=Signal)
    node_deleted: Signal[UUID] = attr.ib(init=False, factory=Signal)
    port_created: Signal[Port] = attr.ib(init=False, factory=Signal)
    port_deleted: Signal[UUID] = attr.ib(init=False, factory=Signal)
    connection_created: Signal[Connection] = attr.ib(init=False, factory=Signal)
    connection_deleted: Signal[UUID] = attr.ib(init=False, factory=Signal)

    def __attrs_post_init__(self) -> None:
        self._root_graph = self.create_graph()
        self._root_serializer = Serializer()
        self._root_deserializer = Deserializer(self)

    def root_graph(self) -> Graph:
        "return the state's root graph"
        return self._root_graph

    def get_graph(self, graph: GraphLike) -> Graph:
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

    def get_node(self, node: NodeLike) -> Node:
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

    def get_port(self, port: PortLike) -> Port:
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

    def get_connection(self, connection: ConnectionLike) -> Connection:
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

        logger.debug("Created graph %s.", graph.uuid())

        self.graph_created.emit(graph)

        return graph

    def delete_graph(self, graph: GraphLike) -> None:
        """Delete a graph and unregister it from the state."""

        graph = self.get_graph(graph)

        del self._graphs[graph.uuid()]

        logger.debug("Deleted graph %s.", graph.uuid())

        self.graph_deleted.emit(graph.uuid())

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
            state=self,
            name=name,
            library=library,
            parent_graph_id=parent_graph_id,
        )
        if node_type:
            node.set_type(node_type)

        self._nodes[node.uuid()] = node

        logger.debug("Created node %s.", node.path())

        self.node_created.emit(node)

        node.post_node_created()

        return node

    def delete_node(self, node: NodeLike) -> None:
        """Delete a node and unregister it from the state."""

        node = self.get_node(node)

        del self._nodes[node.uuid()]

        logger.debug("Deleted node %s.", node.path())

        self.node_deleted.emit(node.uuid())

    def create_port(
        self,
        name: str,
        direction: PortDirection,
        port_type: Type[PortType],
        node: NodeLike,
        graph: GraphLike,
        parent_port: Optional[PortLike] = None,
    ) -> Port[PortType]:
        """Create a port and register it to the state."""

        node = self.get_node(node)
        graph = self.get_graph(graph)

        port = Port(
            self,
            graph.uuid(),
            node.uuid(),
            name,
            direction,
            port_type,
        )

        if parent_port is not None:
            parent_port = self.get_port(parent_port)
            port.set_parent_port(parent_port)
            parent_port.add_child_port(port)

        self._ports[port.uuid()] = port

        logger.debug("Created port %s.", port.path())

        self.port_created.emit(port)

        return port

    def delete_port(self, port: PortLike) -> None:
        """Delete a port and unregister it from the state."""

        port = self.get_port(port)

        del self._ports[port.uuid()]

        logger.debug("Deleted port %s from the state.", port.path())

        self.port_deleted.emit(port.uuid())

    def create_connection(
        self,
        graph: GraphLike,
        source: PortLike,
        target: PortLike,
    ) -> Connection:
        """Create a connection and register it to the state."""

        graph = self.get_graph(graph)
        source = self.get_port(source)
        target = self.get_port(target)

        connection = Connection(self, graph.uuid(), source.uuid(), target.uuid())
        self._connections[connection.uuid()] = connection

        logger.debug("Created connection %s.", connection.uuid())

        self.connection_created.emit(connection)

        return connection

    def delete_connection(self, connection: ConnectionLike) -> None:
        """Delete a connection and unregister it from the state."""

        connection = self.get_connection(connection)

        del self._connections[connection.uuid()]

        logger.debug("Deleted connection %s.", connection.uuid())

        self.connection_deleted.emit(connection.uuid())

    def serializers(self) -> List[Serializer]:
        return self._serializers

    def deserializers(self) -> List[ExternalDeserializer]:
        return self._deserializers

    def register_serializer(self, serializer: ExternalSerializer) -> None:
        self._serializers.append(serializer)
        self._root_serializer.register(serializer)

    def register_deserializer(self, deserializer: ExternalDeserializer) -> None:
        self._deserializers.append(deserializer)
        self._root_deserializer.register(deserializer)

    def serialize(self, root: NodeLike) -> Dict[str, Any]:
        root = self.get_node(root)
        data = self._root_serializer.serialize(root)
        return data

    def deserialize(self, data: Dict[str, Any], graph: GraphLike) -> Node:
        graph = self.get_graph(graph)
        node = self._root_deserializer.deserialize(data, graph)
        return node
