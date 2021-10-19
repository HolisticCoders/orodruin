"""Serialize core objects."""
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

from orodruin.core import Connection, Graph, Node, Port, PortType


class Serializer(metaclass=ABCMeta):
    """Serialize data to save in an Orodruin file."""

    def serialize(self, root: Node) -> Dict:
        data = self.serialize_node(root)

        data["ports"] = [
            self._serialize_port_recursive(port)
            for port in root.ports()
            if not port.parent_port()
        ]

        graph = root.graph()

        if graph:
            data["graph"] = {
                "nodes": [self.serialize(node) for node in graph.nodes()],
                "connections": [
                    self.serialize_connection(connection, root)
                    for connection in graph.connections()
                ],
            }
        return data

    def _serialize_port_recursive(self, port: Port) -> Dict[str, Any]:
        data = self.serialize_port(port)
        if port.child_ports():
            data["children"] = [
                self._serialize_port_recursive(child) for child in port.child_ports()
            ]
        return data

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


class DefaultSerializer(Serializer):
    def serialize_graph(self, graph: Graph) -> Dict[str, Any]:
        return {}

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
        return data

    def serialize_port(self, port: Port) -> Dict[str, Any]:
        return {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
            "value": self._encode_port_value(port.get()),
        }

    def serialize_connection(
        self, connection: Connection, parent_node: Node
    ) -> Dict[str, Any]:
        return {
            "source": str(connection.source().relative_path(parent_node)),
            "target": str(connection.target().relative_path(parent_node)),
        }

    @staticmethod
    def _encode_port_value(port_value: PortType) -> Any:
        try:
            return port_value.value  # type: ignore[attr-defined]
        except AttributeError:
            return port_value
