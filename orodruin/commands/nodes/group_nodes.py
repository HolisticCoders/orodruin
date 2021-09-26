"""Create Node command."""
from dataclasses import dataclass, field
from typing import List

from orodruin.core import Graph, Node
from orodruin.core.graph import GraphLike
from orodruin.core.node import NodeLike
from orodruin.core.state import State

from ..command import Command
from .create_node import CreateNode


@dataclass
class GroupNodes(Command):
    """Create Node command."""

    state: State
    graph: GraphLike
    nodes: List[NodeLike]

    _nodes: List[Node] = field(init=False)
    _graph: Graph = field(init=False)
    _created_node: Node = field(init=False)

    def __post_init__(self) -> None:
        self._nodes = [self.state.node_from_nodelike(node) for node in self.nodes]
        self._graph = self.state.graph_from_graphlike(self.graph)

    def do(self) -> Node:

        self._created_node = CreateNode(self.state, "NewNode", graph=self._graph).do()

        for node in self._nodes:
            self._graph.unregister_node(node.uuid())
            self._created_node.graph().register_node(node)

        return self._created_node

    def undo(self) -> None:
        raise NotImplementedError
