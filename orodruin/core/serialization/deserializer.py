"""Deserialize core objects."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import attr

from orodruin.commands.nodes import CreateNode, ImportNode
from orodruin.commands.ports import ConnectPorts, CreatePort, SetPort
from orodruin.core.library import LibraryManager
from orodruin.core.port import PortDirection, PortTypes
from orodruin.core.utils import port_from_path
from orodruin.exceptions import LibraryDoesNotExistError, PortDoesNotExistError

from .types import SerializationType

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, Node, Port, State


class Deserializer(metaclass=ABCMeta):
    """Deserialize graphs, nodes, ports and connections data."""

    @abstractmethod
    def deserialize_graph(self, data: Dict[str, Any], graph: Graph) -> None:
        """Deserialize data onto an existing graph."""

    @abstractmethod
    def deserialize_node(self, data: Dict[str, Any], node: Node) -> None:
        """Deserialize data onto an existing node."""

    @abstractmethod
    def deserialize_port(self, data: Dict[str, Any], port: Port) -> None:
        """Deserialize data onto an existing port."""

    @abstractmethod
    def deserialize_connection(
        self, data: Dict[str, Any], connection: Connection
    ) -> None:
        """Deserialize data onto an existing connection."""


class OrodruinDeserializer(Deserializer):
    """Deserialize orodruin specific data."""

    def deserialize_graph(self, data: Dict[str, Any], graph: Graph) -> None:
        pass

    def deserialize_node(self, data: Dict[str, Any], node: Node) -> None:
        pass

    def deserialize_port(self, data: Dict[str, Any], port: Port) -> None:
        """Set the port value."""
        serialization_type = SerializationType(data["metadata"]["serialization_type"])
        if serialization_type is SerializationType.instance:
            SetPort(port, data["value"]).do()

    def deserialize_connection(
        self, data: Dict[str, Any], connection: Connection
    ) -> None:
        pass


@attr.s
class RootDeserializer:
    """Deserialize data from an Orodruin file."""

    state: State = attr.ib()

    def _state_deserializers(self) -> List[Deserializer]:
        return self.state.deserializers()

    def deserialize(self, data: Dict[str, Any], graph: Graph) -> Node:
        """Recursively deserialize a node's data."""
        node = self.deserialize_node(data, graph)

        for port_data in data.get("ports", []):
            self._deserialize_port_recursive(port_data, node)

        metadata = data["metadata"]
        serialization_type = SerializationType(metadata["serialization_type"])

        if serialization_type is SerializationType.definition:
            # deserialize the node's graph only if we're in a definition
            # otherwise the sub nodes will be created durint both
            # the definition _and_ the instance deserialization of the node.

            for child_data in data.get("graph", {}).get("nodes", []):
                self.deserialize(child_data, node.graph())

            for connection_data in data.get("graph", {}).get("connections", []):
                self.deserialize_connection(connection_data, node)

            node_graph = node.graph()
            if node_graph:
                for deserializer in self._state_deserializers():
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
        """Create a node, or import it from a library."""
        library_name = data["library"]
        if library_name != "Internal":

            library = LibraryManager.find_library(library_name)

            if library is None:
                raise LibraryDoesNotExistError(
                    f"Found no registered library called {library_name}"
                )

            library_name = library.name()

        else:
            library = None

        metadata = data["metadata"]
        serialization_type = SerializationType(metadata["serialization_type"])

        if serialization_type is SerializationType.definition:

            node = CreateNode(
                state=self.state,
                name=data["name"],
                type=data["type"],
                library=library,
                graph=graph,
            ).do()

        else:

            node = ImportNode(self.state, graph, data["type"], library_name).do()
            node.set_name(data["name"])

        for deserializer in self._state_deserializers():
            deserializer.deserialize_node(data, node)

        return node

    def deserialize_port(
        self, data: Dict[str, Any], node: Node, parent: Optional[Port] = None
    ) -> Port:
        """Create a port, and/or deserialize its data."""

        name = data["name"]

        serialization_type = SerializationType(data["metadata"]["serialization_type"])

        if serialization_type is SerializationType.definition:

            direction = PortDirection[data["direction"]]
            port_type = PortTypes[data["type"]].value
            port = CreatePort(self.state, node, name, direction, port_type, parent).do()

        else:

            port = node.port(name)

        for deserializer in self._state_deserializers():
            deserializer.deserialize_port(data, port)

        return port

    def deserialize_connection(
        self, data: Dict[str, Any], parent_node: Node
    ) -> Connection:
        """Create a connection."""
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

        for deserializer in self._state_deserializers():
            deserializer.deserialize_connection(data, connection)

        return connection
