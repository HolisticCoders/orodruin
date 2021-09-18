"""Create Port command."""
from dataclasses import dataclass, field
from typing import Type

from orodruin.core import Component, Graph, Port, PortDirection

from ..command import Command


@dataclass
class CreatePort(Command):
    """Create Port command."""

    graph: Graph
    component: Component
    name: str
    direction: PortDirection
    type: Type

    _created_port: Port = field(init=False)

    def do(self) -> Port:
        port = Port(
            _name=self.name,
            _direction=self.direction,
            _type=self.type,
            _component=self.component,
        )

        self.graph.register_port(port)
        self.component.register_port(port)
        self._created_port = port
        return self._created_port

    def undo(self) -> None:
        # TODO: Delete all the connections from/to this Port
        self.graph.unregister_port(self._created_port.uuid())
        self.component.unregister_port(self._created_port.uuid())

    def redo(self) -> Port:
        # TODO: Recreate all the connections from/to this Port
        self.graph.register_port(self._created_port)
        self.component.register_port(self._created_port)
        return self._created_port
