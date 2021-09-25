"""Create Port command."""
from dataclasses import dataclass, field
from typing import Type

from orodruin.core import Node, Graph, Port, PortDirection
from orodruin.core.state import State

from ..command import Command


@dataclass
class CreatePort(Command):
    """Create Port command."""

    state: State
    node: Node
    name: str
    direction: PortDirection
    type: Type

    _graph: Graph = field(init=False)
    _created_port: Port = field(init=False)

    def __post_init__(self) -> None:
        self._graph = self.node.parent_graph()

    def do(self) -> Port:
        port = self.state.create_port(
            self.name, self.direction, self.type, self.node.uuid()
        )

        self._graph.register_port(port)
        self.node.register_port(port)
        self._created_port = port

        return self._created_port

    def undo(self) -> None:
        raise NotImplementedError
        # TODO: Delete all the connections from/to this Port
        self._graph.unregister_port(self._created_port)
        self.node.unregister_port(self._created_port)

    # def redo(self) -> None:
    #     raise NotImplementedError
    #     # TODO: Recreate all the connections from/to this Port
    #     self._graph.register_port(self._created_port)
    #     self.node.register_port(self._created_port)
