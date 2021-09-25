"""Export Node command"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from orodruin.core import Node, LibraryManager, Port
from orodruin.exceptions import LibraryDoesNotExistError

from ..command import Command


@dataclass
class ExportNode(Command):
    """Export Node command"""

    node: Node
    library_name: str
    target_name: str = "orodruin"
    node_name: Optional[str] = None

    _exported_path: Path = field(init=False)

    def do(self) -> Path:
        library = LibraryManager.find_library(self.library_name)

        if not library:
            raise LibraryDoesNotExistError(
                f"Found no registered library called {self.library_name}"
            )

        if not self.node_name:
            self.node_name = self.node.name()

        self._exported_path = (
            library.path() / self.target_name / f"{self.node_name}.json"
        )

        with self._exported_path.open("w") as f:
            serialized_node = self._node_as_json(self.node)
            f.write(serialized_node)

        return self._exported_path

    def undo(self) -> None:
        """Command is not undoable."""

    @classmethod
    def _node_as_json(cls, node: Node) -> str:
        """Returns the serialized representation of the node."""
        return json.dumps(
            cls._node_definition_data(node),
            indent=4,
        )

    @classmethod
    def _node_definition_data(cls, node: Node) -> Dict[str, Any]:
        """Returns a dict representing the given Node definition.

        This is recursively called on all the subnodes,
        returning a dict that represents the entire rig.
        """
        data = {
            "definitions": cls._sub_node_definitions(node),
            "nodes": cls._sub_node_instances(node),
            "ports": cls._serialize_ports(node),
            "connections": cls._node_connections(node),
        }
        return data

    @classmethod
    def _sub_node_definitions(cls, node: Node) -> Dict:
        definitions_data = {}

        for sub_node in node.graph().nodes():
            if sub_node.library():
                continue

            if sub_node.type() not in definitions_data:
                definition_data = cls._node_definition_data(sub_node)
                definitions_data[str(sub_node.type())] = definition_data

        return definitions_data

    @classmethod
    def _sub_node_instances(cls, node: Node) -> List:
        nodes_data = []

        for sub_node in node.graph().nodes():
            instance_data = cls._node_instance_data(sub_node)
            nodes_data.append(instance_data)

        return nodes_data

    @classmethod
    def _node_instance_data(cls, node: Node) -> Dict[str, Any]:
        """Return the data representation of the instanced node."""
        library = node.library()

        if library is None:
            library_name = "Internal"
        else:
            library_name = library.name()

        data = {
            "type": f"{library_name}::{node.type()}",
            "name": node.name(),
            "ports": {p.name(): p.get() for p in node.ports()},
        }
        return data

    @classmethod
    def _serialize_ports(cls, node: Node) -> List[Dict[str, str]]:
        ports_data = []

        for port in node.ports():
            ports_data.append(cls._port_definition_data(port))

        return ports_data

    @classmethod
    def _port_definition_data(cls, port: Port) -> Dict[str, str]:
        """Returns a dict representing the given Port definition."""
        data = {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
        }
        return data

    @classmethod
    def _node_connections(cls, node: Node) -> List[Tuple[str, str]]:
        connection_data = []
        for connection in node.graph().connections():
            connection_data.append(
                (
                    str(connection.source().relative_path(node)),
                    str(connection.target().relative_path(node)),
                )
            )
        return connection_data
