"""Delete Port command."""
from dataclasses import dataclass, field
from uuid import UUID

from orodruin.core import Component, Graph, Port

from ..command import Command


@dataclass
class DeletePort(Command):
    """Delete Port command."""

    graph: Graph
    port_id: UUID

    _deleted_port: Port = field(init=False)
    _owner_component: Component = field(init=False)

    def do(self) -> None:
        # TODO: Delete all the connections from/to this component
        self._deleted_port = self.graph.unregister_port(self.port_id)
        self._owner_component = self._deleted_port.component()
        self._owner_component.unregister_port(self.port_id)

    def undo(self) -> None:
        # TODO: Recreate all the connections from/to this component
        self.graph.register_port(self._deleted_port)
        self._owner_component.register_port(self._deleted_port)
