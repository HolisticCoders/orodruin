"""Delete Node command."""
from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from ..command import Command
from ..ports import DeletePort, DisconnectPorts

if TYPE_CHECKING:
    from orodruin.core import Graph, Node, NodeLike, State


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
            for connection in port.connections():
                DisconnectPorts(
                    self.state,
                    self._graph,
                    connection.source(),
                    connection.target(),
                ).do()

        for port in self._node.ports():
            DeletePort(self.state, port).do()

        self._graph.unregister_node(self._node)
        self.state.delete_node(self._node)

    def undo(self) -> None:
        raise NotImplementedError
