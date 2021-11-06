"""Serialize core objects."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

import attr

from .types import SerializationType

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, Node, Port, PortType, State


class Serializer(metaclass=ABCMeta):
    """Serialize graphs, nodes, ports and connections data."""

    @abstractmethod
    def serialize_graph(
        self, graph: Graph, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a graph's data."""

    @abstractmethod
    def serialize_node(
        self, node: Node, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a node's data."""

    @abstractmethod
    def serialize_port(
        self, port: Port, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a port's data."""

    @abstractmethod
    def serialize_connection(
        self,
        connection: Connection,
        parent_node: Node,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        """Serialize a connection's data."""


@attr.s
class RootSerializer:
    """Serialize data to save in an Orodruin file."""

    state: State = attr.ib()

    def _state_serializers(self) -> List[Serializer]:
        return self.state.serializers()

    def serialize(self, root: Node, serialization_type: SerializationType) -> Dict:
        """Recursively serialize a node's data."""
        data = self.serialize_node(root, serialization_type)

        data["ports"] = [
            self._serialize_port_recursive(port, serialization_type)
            for port in root.ports()
            if not port.parent_port()
        ]

        node_graph = root.graph()

        if node_graph:
            graph_data = self.serialize_graph(node_graph, SerializationType.instance)
            data["graph"] = graph_data

        return data

    def _serialize_port_recursive(
        self, port: Port, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        data = self.serialize_port(port, serialization_type)
        if port.child_ports():
            data["children"] = [
                self._serialize_port_recursive(child, serialization_type)
                for child in port.child_ports()
            ]
        return data

    def serialize_graph(
        self, graph: Graph, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a graph's data."""
        parent_node = graph.parent_node()
        if not parent_node:
            raise NotImplementedError("Cannot serialize a graph with no parent node.")

        graph_data = {}

        nodes_data = []
        for node in graph.nodes():
            serialization_type = (
                SerializationType.instance
                if node.library()
                else SerializationType.definition
            )
            nodes_data.append(self.serialize(node, serialization_type))
        graph_data["nodes"] = nodes_data

        graph_data["connections"] = [
            self.serialize_connection(
                connection, parent_node, SerializationType.instance
            )
            for connection in graph.connections()
        ]

        for serializer in self._state_serializers():
            serializer_data = serializer.serialize_graph(graph, serialization_type)
            graph_data.update(serializer_data)

        return graph_data

    def serialize_node(
        self, node: Node, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a node's data."""
        library = node.library()

        if library is None:
            library_name = "Internal"
        else:
            library_name = library.name()

        data = {
            "name": node.name(),
            "type": node.type(),
            "library": library_name,
            "metadata": {
                "serialization_type": serialization_type.value,
            },
        }

        for serializer in self._state_serializers():
            serializer_data = serializer.serialize_node(node, serialization_type)
            data.update(serializer_data)

        return data

    def serialize_port(
        self, port: Port, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        """Serialize a port's data."""
        data = {
            "name": port.name(),
            "metadata": {
                "serialization_type": serialization_type.value,
            },
        }

        if serialization_type is SerializationType.definition:
            data["direction"] = port.direction().name
            data["type"] = port.type().__name__

        if serialization_type is SerializationType.instance:
            data["value"] = self._encode_port_value(port.get())

        for serializer in self._state_serializers():
            serializer_data = serializer.serialize_port(port, serialization_type)
            data.update(serializer_data)

        return data

    def serialize_connection(
        self,
        connection: Connection,
        parent_node: Node,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        """Serialize a connection's data."""
        data = {
            "source": str(connection.source().relative_path(parent_node)),
            "target": str(connection.target().relative_path(parent_node)),
        }

        for serializer in self._state_serializers():
            serializer_data = serializer.serialize_connection(
                connection, parent_node, serialization_type
            )
            data.update(serializer_data)

        return data

    @staticmethod
    def _encode_port_value(port_value: PortType) -> Any:
        try:
            return port_value.value  # type: ignore[attr-defined]
        except AttributeError:
            return port_value
