"""Create Port command."""
from dataclasses import dataclass, field
from typing import Optional, Type

from orodruin.core import Graph, Node, NodeLike, Port, PortDirection, State
from orodruin.core.port.port import PortLike
from orodruin.core.utils import get_unique_port_name

from ..command import Command


@dataclass
class CreatePort(Command):
    """Create Port command."""

    state: State
    node: NodeLike
    name: str
    direction: PortDirection
    type: Type
    parent_port: Optional[PortLike] = None

    _node: Node = field(init=False)
    _graph: Graph = field(init=False)
    _created_port: Port = field(init=False)
    _parent_port: Optional[Port] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._node = self.state.get_node(self.node)
        parent_graph = self._node.parent_graph()

        if not parent_graph:
            raise TypeError("Cannot create a Port on a node with no graph.")

        self._graph = parent_graph

        if self.parent_port:
            self._parent_port = self.state.get_port(self.parent_port)
        else:
            self._parent_port = None

    def do(self) -> Port:
        unique_name = get_unique_port_name(self._node, self.name)

        port = self.state.create_port(
            unique_name,
            self.direction,
            self.type,
            self._node,
            self._graph,
            self._parent_port,
        )

        self._graph.register_port(port)
        self._node.register_port(port)
        self._created_port = port

        return self._created_port

    def undo(self) -> None:
        raise NotImplementedError
