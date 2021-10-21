"""Serialize core objects."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

import attr

from orodruin.core import Connection, Graph, Node, Port, PortType


@attr.s
class Serializer:
    """Serialize data to save in an Orodruin file."""

    _serializers: List[ExternalSerializer] = attr.ib(init=False, factory=list)

    def register(self, serializer: ExternalSerializer):
        self._serializers.append(serializer)

    def serialize(self, root: Node) -> Dict:
        data = self.serialize_node(root)

        data["ports"] = [
            self._serialize_port_recursive(port)
            for port in root.ports()
            if not port.parent_port()
        ]

        node_graph = root.graph()

        if node_graph:

            graph_data = {
                "nodes": [self.serialize(node) for node in node_graph.nodes()],
                "connections": [
                    self.serialize_connection(connection, root)
                    for connection in node_graph.connections()
                ],
            }

            for serializer in self._serializers:
                serializer_data = serializer.serialize_graph(node_graph)
                graph_data.update(serializer_data)

            data["graph"] = graph_data

        return data

    def _serialize_port_recursive(self, port: Port) -> Dict[str, Any]:
        data = self.serialize_port(port)
        if port.child_ports():
            data["children"] = [
                self._serialize_port_recursive(child) for child in port.child_ports()
            ]
        return data

    def serialize_node(self, node: Node) -> Dict[str, Any]:
        library = node.library()

        if library is None:
            library_name = "Internal"
        else:
            library_name = library.name()

        data = {
            "name": node.name(),
            "type": node.type(),
            "library": library_name,
        }

        for serializer in self._serializers:
            serializer_data = serializer.serialize_node(node)
            data.update(serializer_data)

        return data

    def serialize_port(self, port: Port) -> Dict[str, Any]:
        data = {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
            "value": self._encode_port_value(port.get()),
        }

        for serializer in self._serializers:
            serializer_data = serializer.serialize_port(port)
            data.update(serializer_data)

        return data

    def serialize_connection(
        self, connection: Connection, parent_node: Node
    ) -> Dict[str, Any]:
        data = {
            "source": str(connection.source().relative_path(parent_node)),
            "target": str(connection.target().relative_path(parent_node)),
        }

        for serializer in self._serializers:
            serializer_data = serializer.serialize_connection(connection, parent_node)
            data.update(serializer_data)

        return data

    @staticmethod
    def _encode_port_value(port_value: PortType) -> Any:
        try:
            return port_value.value  # type: ignore[attr-defined]
        except AttributeError:
            return port_value


class ExternalSerializer(metaclass=ABCMeta):
    @abstractmethod
    def serialize_graph(self, graph: Graph) -> Dict[str, Any]:
        pass

    @abstractmethod
    def serialize_node(self, node: Node) -> Dict[str, Any]:
        pass

    @abstractmethod
    def serialize_port(self, port: Port) -> Dict[str, Any]:
        pass

    @abstractmethod
    def serialize_connection(
        self, connection: Connection, parent_node: Node
    ) -> Dict[str, Any]:
        pass
