"""Import Node command."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import attr

from orodruin.core.library import LibraryManager
from orodruin.exceptions import LibraryDoesNotExistError, NodeNotFoundError

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Graph, GraphLike, Node, State


@attr.s
class ImportNode(Command):
    """Import Node command."""

    state: State = attr.ib()
    graph: GraphLike = attr.ib()
    node_type: str = attr.ib()
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

        node_path = library.find_node(self.node_type, self.target_name)

        if not node_path:
            raise NodeNotFoundError(
                f"Found no node '{self.node_type}' in library '{self.library_name}' "
                f"for target '{self.target_name}'"
            )

        with open(node_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        self._imported_node = self.state.deserialize(data, self._graph)

        return self._imported_node

    def undo(self) -> None:
        """Command is not undoable."""
