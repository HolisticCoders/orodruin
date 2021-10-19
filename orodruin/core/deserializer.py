"""Deserialize core objects."""
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

import attr

from orodruin.commands.ports import ConnectPorts, CreatePort
from orodruin.commands.nodes import CreateNode
from orodruin.core import (
    Connection,
    Graph,
    LibraryManager,
    Node,
    Port,
    PortDirection,
    PortTypes,
    State,
)
from orodruin.core.utils import port_from_path
from orodruin.exceptions import (
    LibraryDoesNotExistError,
    PortDoesNotExistError,
)


class Deserializer(metaclass=ABCMeta):
    """Deserialize data from an Orodruin file."""

    def deserialize(self, data: Dict[str, Any], graph: Graph) -> Node:
        node = self.deserialize_node(data, graph)

        for port_data in data.get("ports", []):
            self._deserialize_port_recursive(port_data, node)

        for child_data in data.get("graph", {}).get("nodes", []):
            self.deserialize(child_data, node.graph())

        for connection_data in data.get("graph", {}).get("connections", []):
            self.deserialize_connection(connection_data, node)

        return node

    def _deserialize_port_recursive(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        port = self.deserialize_port(data, node, parent)
        for child_data in data.get("children", []):
            self._deserialize_port_recursive(child_data, node, port)
        return port

    @abstractmethod
    def deserialize_graph(self, data: Dict[str, Any]) -> Graph:
        pass

    @abstractmethod
    def deserialize_node(self, data: Dict[str, Any], graph: Graph) -> Node:
        pass

    @abstractmethod
    def deserialize_port(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        pass

    @abstractmethod
    def deserialize_connection(
        self, data: Dict[str, Any], parent_node: Node
    ) -> Connection:
        pass


@attr.s
class DefaultDeserializer(Deserializer):

    state: State = attr.ib()

    def deserialize_graph(self, data: Dict[str, Any]) -> Graph:
        return super().deserialize_graph(data)

    def deserialize_node(self, data: Dict[str, Any], graph: Graph) -> Node:
        library = LibraryManager.find_library(data["library"])

        if not library and data["library"] != "Internal":
            raise LibraryDoesNotExistError(
                f"Found no registered library called {data['library']}"
            )

        return CreateNode(
            state=self.state,
            graph=graph,
            name=data["name"],
            type=data["type"],
            library=library,
        ).do()

    def deserialize_port(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        name = data["name"]
        direction = PortDirection[data["direction"]]
        port_type = PortTypes[data["type"]].value
        return CreatePort(self.state, node, name, direction, port_type, parent).do()

    def deserialize_connection(
        self, data: Dict[str, Any], parent_node: Node
    ) -> Connection:
        source_name = data["source"]
        target_name = data["target"]

        source_port = port_from_path(parent_node, source_name)
        target_port = port_from_path(parent_node, target_name)

        if not source_port:
            raise PortDoesNotExistError(f"Port {source_name} not found")
        if not target_port:
            raise PortDoesNotExistError(f"Port {target_name} not found")

        return ConnectPorts(
            self.state, parent_node.graph(), source_port, target_port
        ).do()
