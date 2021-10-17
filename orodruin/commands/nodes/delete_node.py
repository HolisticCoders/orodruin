"""Delete Node command."""
import attr

from orodruin.core import Graph, Node, NodeLike, State
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import DeletePort, DisconnectPorts


@attr.s
class DeleteNode(Command):
    """Delete Node command."""

    state: State = attr.ib()
    node: NodeLike = attr.ib()

    _node: Node = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._node = self.state.get_node(self.node)
        parent_graph = self._node.parent_graph()

        if not parent_graph:
            raise TypeError("Cannot create a Port on a node with no graph.")

        self._graph = parent_graph

    def do(self) -> None:
        for node in self._node.graph().nodes():
            DeleteNode(self.state, node).do()

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
