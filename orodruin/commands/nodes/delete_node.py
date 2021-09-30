"""Delete Node command."""
from dataclasses import dataclass, field

from orodruin.core import Graph, Node, NodeLike, State
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import DeletePort, DisconnectPorts


@dataclass
class DeleteNode(Command):
    """Delete Node command."""

    state: State
    node: NodeLike

    _node: Node = field(init=False)
    _graph: Graph = field(init=False)

    def __post_init__(self) -> None:
        self._node = self.state.node_from_nodelike(self.node)
        parent_graph = self._node.parent_graph()

        if not parent_graph:
            raise TypeError("Cannot create a Port on a node with no graph.")

        self._graph = parent_graph

    def do(self) -> None:
        for port in self._node.ports():
            for connection in list_connections(self._graph, port):
                DisconnectPorts(
                    self.state,
                    self._graph,
                    connection.source(),
                    connection.target(),
                ).do()

            DeletePort(self.state, port).do()

        self._graph.unregister_node(self._node)
        self.state.delete_node(self._node)

    def undo(self) -> None:
        raise NotImplementedError
