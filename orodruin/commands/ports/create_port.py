"""Create Port command."""
from __future__ import annotations
from typing import Optional, Type, TYPE_CHECKING

import attr

from orodruin.core.utils import get_unique_port_name

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import (
        Graph,
        Node,
        NodeLike,
        Port,
        PortDirection,
        PortLike,
        State,
    )


@attr.s
class CreatePort(Command):
    """Create Port command."""

    state: State = attr.ib()
    node: NodeLike = attr.ib()
    name: str = attr.ib()
    direction: PortDirection = attr.ib()
    type: Type = attr.ib()
    parent_port: Optional[PortLike] = attr.ib(default=None)

    _node: Node = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)
    _created_port: Port = attr.ib(init=False)
    _parent_port: Optional[Port] = attr.ib(init=False, default=None)

    def __attrs_post_init__(self) -> None:
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
