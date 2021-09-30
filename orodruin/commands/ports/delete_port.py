"""Delete Port command."""
from dataclasses import dataclass, field

from orodruin.core import Graph, Node, Port, PortLike, State

from ..command import Command


@dataclass
class DeletePort(Command):
    """Delete Port command."""

    state: State
    port: PortLike

    _port: Port = field(init=False)
    _graph: Graph = field(init=False)
    _node: Node = field(init=False)

    def __post_init__(self) -> None:
        self._port = self.state.port_from_portlike(self.port)
        self._graph = self._port.graph()
        self._node = self._port.node()

    def do(self) -> None:
        # TODO: Delete all the connections from/to this node
        self._node.unregister_port(self.port)
        self._graph.unregister_port(self.port)
        self.state.delete_port(self.port)

    def undo(self) -> None:
        raise NotImplementedError
