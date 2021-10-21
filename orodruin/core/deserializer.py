"""Deserialize core objects."""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

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
)
from orodruin.core.utils import port_from_path
from orodruin.exceptions import (
    LibraryDoesNotExistError,
    PortDoesNotExistError,
)

if TYPE_CHECKING:
    from orodruin.core import State


@attr.s
class Deserializer:
    """Deserialize data from an Orodruin file."""

    state: State = attr.ib()
    _deserializers: List[ExternalDeserializer] = attr.ib(init=False, factory=list)

    def register(self, deserializer: ExternalDeserializer):
        self._deserializers.append(deserializer)

    def deserialize(self, data: Dict[str, Any], graph: Graph) -> Node:
        node = self.deserialize_node(data, graph)

        for port_data in data.get("ports", []):
            self._deserialize_port_recursive(port_data, node)

        for child_data in data.get("graph", {}).get("nodes", []):
            self.deserialize(child_data, node.graph())

        for connection_data in data.get("graph", {}).get("connections", []):
            self.deserialize_connection(connection_data, node)

        node_graph = node.graph()
        if node_graph:
            for deserializer in self._deserializers:
                deserializer.deserialize_graph(data, node_graph)

        return node

    def _deserialize_port_recursive(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        port = self.deserialize_port(data, node, parent)
        for child_data in data.get("children", []):
            self._deserialize_port_recursive(child_data, node, port)
        return port

    def deserialize_node(self, data: Dict[str, Any], graph: Graph) -> Node:
        library = LibraryManager.find_library(data["library"])

        if not library and data["library"] != "Internal":
            raise LibraryDoesNotExistError(
                f"Found no registered library called {data['library']}"
            )

        node = CreateNode(
            state=self.state,
            graph=graph,
            name=data["name"],
            type=data["type"],
            library=library,
        ).do()

        for deserializer in self._deserializers:
            deserializer.deserialize_node(data, node)

        return node

    def deserialize_port(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        name = data["name"]
        direction = PortDirection[data["direction"]]
        port_type = PortTypes[data["type"]].value
        port = CreatePort(self.state, node, name, direction, port_type, parent).do()

        for deserializer in self._deserializers:
            deserializer.deserialize_port(data, port)

        return port

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

        connection = ConnectPorts(
            self.state, parent_node.graph(), source_port, target_port
        ).do()

        for deserializer in self._deserializers:
            deserializer.deserialize_connection(data, connection)

        return connection


class ExternalDeserializer(metaclass=ABCMeta):
    @abstractmethod
    def deserialize_graph(self, data: Dict[str, Any], graph: Graph) -> None:
        pass

    @abstractmethod
    def deserialize_node(self, data: Dict[str, Any], node: Node) -> None:
        pass

    @abstractmethod
    def deserialize_port(self, data: Dict[str, Any], port: Port) -> None:
        pass

    @abstractmethod
    def deserialize_connection(
        self, data: Dict[str, Any], connection: Connection
    ) -> None:
        pass
