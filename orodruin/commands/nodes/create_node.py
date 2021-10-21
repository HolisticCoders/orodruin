"""Create Node command."""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import attr

from orodruin.core.utils import get_unique_node_name

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Graph, GraphLike, Library, Node, State


@attr.s
class CreateNode(Command):
    """Create Node command."""

    state: State = attr.ib()
    name: str = attr.ib()
    type: Optional[str] = attr.ib(default=None)
    library: Optional[Library] = attr.ib(default=None)
    graph: Optional[GraphLike] = attr.ib(default=None)

    _graph: Graph = attr.ib(init=False)
    _created_node: Node = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        if self.graph:
            self._graph = self.state.get_graph(self.graph)
        else:
            self._graph = self.state.root_graph()

    def do(self) -> Node:
        unique_name = get_unique_node_name(self._graph, self.name)

        node = self.state.create_node(
            name=unique_name,
            parent_graph_id=self._graph.uuid(),
            library=self.library,
            node_type=self.type,
        )

        self._graph.register_node(node)
        self._created_node = node

        return self._created_node

    def undo(self) -> None:
        raise NotImplementedError
