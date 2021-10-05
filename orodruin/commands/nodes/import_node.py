"""Import Node command."""
import json
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple

from orodruin.core import (
    Graph,
    GraphLike,
    Library,
    LibraryManager,
    Node,
    Port,
    PortDirection,
    State,
)
from orodruin.core.port import types as port_types
from orodruin.core.utils import port_from_path
from orodruin.exceptions import (
    LibraryDoesNotExistError,
    NodeNotFoundError,
    PortDoesNotExistError,
)

from ..command import Command
from ..ports import ConnectPorts, CreatePort, SetPort
from .create_node import CreateNode


@dataclass
class ImportNode(Command):
    """Import Node command."""

    state: State
    graph: GraphLike
    node_name: str
    library_name: str
    target_name: str = "orodruin"

    _graph: Graph = field(init=False)
    _imported_node: Node = field(init=False)

    def __post_init__(self) -> None:
        self._graph = self.state.graph_from_graphlike(self.graph)

    def do(self) -> Node:
        library = LibraryManager.find_library(self.library_name)

        if not library:
            raise LibraryDoesNotExistError(
                f"Found no registered library called {self.library_name}"
            )

        node_path = library.find_node(self.node_name, self.target_name)

        if not node_path:
            raise NodeNotFoundError(
                f"Found no node in library {self.library_name} "
                f"for target {self.target_name}"
            )

        self._imported_node = self._node_from_json(
            self.state,
            self._graph,
            node_path,
            self.node_name,
            self.node_name,
            library,
        )

        return self._imported_node

    def undo(self) -> None:
        """Command is not undoable."""

    @classmethod
    def _node_from_json(
        cls,
        state: State,
        graph: Graph,
        node_path: PathLike,
        node_name: str,
        node_type: Optional[str] = None,
        library: Optional[Library] = None,
    ) -> "Node":
        """Create a node from its json representation."""
        with open(node_path, "r", encoding="utf-8") as handle:
            node_data = json.loads(handle.read())

        return cls._node_from_data(
            state,
            graph,
            node_data,
            node_name,
            node_type,
            library,
        )

    @classmethod
    def _node_from_data(
        cls,
        state: State,
        graph: Graph,
        node_data: Dict[str, Any],
        node_name: str,
        node_type: Optional[str] = None,
        library: Optional[Library] = None,
    ) -> Node:
        """Create a node from its serialized data."""
        node = CreateNode(
            state=state,
            graph=graph,
            name=node_name,
            type=node_type,
            library=library,
        ).do()

        cls._create_ports(state, node, node_data["ports"])

        cls._create_subnodes(
            state,
            node,
            node_data["nodes"],
            node_data["definitions"],
        )
        cls._create_connections(
            state,
            node,
            node_data["connections"],
        )

        return node

    @classmethod
    def _create_ports(
        cls,
        state: State,
        node: Node,
        ports_data: Dict,
        parent_port: Optional[Port] = None,
    ) -> None:
        for port_data in ports_data:
            name = port_data["name"]
            direction = PortDirection[port_data["direction"]]

            try:
                port_type = getattr(port_types, port_data["type"])
            except AttributeError as error:
                raise NameError(
                    f"Type {port_data['type']} is not registered as an "
                    "orodruin port type"
                ) from error

            port = CreatePort(state, node, name, direction, port_type, parent_port).do()

            children_data = port_data.get("children", [])
            if children_data:
                cls._create_ports(state, node, children_data, port)

    @classmethod
    def _create_subnodes(
        cls,
        state: State,
        node: Node,
        subnodes_data: Dict,
        internal_definitions: Dict,
    ) -> None:
        for subnode_data in subnodes_data:
            library_name, subnode_type = subnode_data["type"].split("::")
            subnode_name = subnode_data["name"]

            if library_name == "Internal":
                subnode_definition = internal_definitions[subnode_type]
                sub_node = cls._node_from_data(
                    state,
                    node.graph(),
                    subnode_definition,
                    subnode_name,
                    subnode_type,
                )
            else:
                sub_node = ImportNode(
                    state,
                    node.graph(),
                    subnode_type,
                    library_name,
                ).do()
                sub_node.set_name(subnode_name)

            for port_name, port_value in subnode_data["ports"].items():
                SetPort(sub_node.port(port_name), port_value).do()

    @classmethod
    def _create_connections(
        cls,
        state: State,
        node: Node,
        connections_data: List[Tuple[str, str]],
    ) -> None:

        for connection in connections_data:
            source_name = connection[0]
            target_name = connection[1]

            source_port = port_from_path(node, source_name)
            target_port = port_from_path(node, target_name)

            if not source_port:
                raise PortDoesNotExistError(f"Port {source_name} not found")
            if not target_port:
                raise PortDoesNotExistError(f"Port {target_name} not found")

            ConnectPorts(state, node.graph(), source_port, target_port).do()
