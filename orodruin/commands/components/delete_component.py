"""Delete Component command."""
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from orodruin.core import Component, Graph
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import DeletePort, DisconnectPorts


@dataclass
class DeleteComponent(Command):
    """Delete Component command."""

    graph: Graph
    component_id: UUID

    _deleted_component: Optional[Component] = field(init=False)
    _command_stack: List[Command] = field(default_factory=list)

    def do(self) -> None:
        self._deleted_component = self.graph.component_from_uuid(self.component_id)

        if not self._deleted_component:
            return

        for port in self._deleted_component.ports():
            for connection in list_connections(self.graph, port):
                command: Command = DisconnectPorts(
                    self.graph,
                    connection.source(),
                    connection.target(),
                )
                self._command_stack.append(command)
                command.do()

            command = DeletePort(self.graph, port.uuid())
            self._command_stack.append(command)
            command.do()

        self.graph.unregister_component(self.component_id)

    def undo(self) -> None:
        if self._deleted_component:
            for cmd in reversed(self._command_stack):
                cmd.undo()
            self.graph.register_component(self._deleted_component)
