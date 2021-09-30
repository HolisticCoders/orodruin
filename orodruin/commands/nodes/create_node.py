"""Create Node command."""
from dataclasses import dataclass, field
from typing import Optional

from orodruin.core import Graph, Library, Node
from orodruin.core.graph import GraphLike
from orodruin.core.state import State
from orodruin.core.utils import get_unique_name

from ..command import Command


@dataclass
class CreateNode(Command):
    """Create Node command."""

    state: State
    name: str
    type: Optional[str] = None
    library: Optional[Library] = None
    graph: Optional[GraphLike] = None

    _graph: Graph = field(init=False)
    _created_node: Node = field(init=False)

    def __post_init__(self) -> None:
        if self.graph:
            self._graph = self.state.graph_from_graphlike(self.graph)
        else:
            self._graph = self.state.root_graph()

    def do(self) -> Node:
        unique_name = get_unique_name(self._graph, self.name)

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
