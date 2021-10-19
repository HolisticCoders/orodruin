"""Import Node command."""
import json
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple

import attr

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
from orodruin.core.deserializer import DefaultDeserializer
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


@attr.s
class ImportNode(Command):
    """Import Node command."""

    state: State = attr.ib()
    graph: GraphLike = attr.ib()
    node_name: str = attr.ib()
    library_name: str = attr.ib()
    target_name: str = attr.ib(default="orodruin")

    _graph: Graph = attr.ib(init=False)
    _imported_node: Node = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._graph = self.state.get_graph(self.graph)

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

        deserializer = DefaultDeserializer(self.state)

        with open(node_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        self._imported_node = deserializer.deserialize(data, self._graph)

        return self._imported_node

    def undo(self) -> None:
        """Command is not undoable."""
