"""Delete Port command."""
from dataclasses import dataclass, field
from uuid import UUID

from orodruin.port.port import Port

from ...component import Component
from ...graph import Graph
from ..command import Command


@dataclass
class DeletePort(Command):
    """Delete Port command."""

    _graph: Graph
    _port_id: UUID

    _deleted_port: Port = field(init=False)
    _owner_component: Component = field(init=False)

    def do(self) -> None:
        # TODO: Delete all the connections from/to this component
        self._deleted_port = self._graph.unregister_port(self._port_id)
        self._owner_component = self._deleted_port.component()
        self._owner_component.unregister_port(self._port_id)

    def undo(self) -> Port:
        # TODO: Recreate all the connections from/to this component
        self._graph.register_port(self._deleted_port)
        self._owner_component.register_port(self._deleted_port)
        return self._deleted_port
