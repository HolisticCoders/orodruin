"""Delete Port command."""
from __future__ import annotations
from typing import TYPE_CHECKING
import attr


from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Graph, Node, Port, PortLike, State


@attr.s
class DeletePort(Command):
    """Delete Port command."""

    state: State = attr.ib()
    port: PortLike = attr.ib()

    _port: Port = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)
    _node: Node = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._port = self.state.get_port(self.port)
        self._graph = self._port.graph()
        self._node = self._port.node()

    def do(self) -> None:
        # TODO: Delete all the connections from/to this node
        self._node.unregister_port(self.port)
        self._graph.unregister_port(self.port)
        self.state.delete_port(self.port)

    def undo(self) -> None:
        raise NotImplementedError
