"""Delete Component command."""
from dataclasses import dataclass, field
from uuid import UUID

from ...component import Component
from ...graph import Graph
from ..command import Command


@dataclass
class DeleteComponent(Command):
    """Delete Component command."""

    graph: Graph
    component_id: UUID

    _deleted_component: Component = field(init=False)

    def do(self) -> None:
        # TODO: Delete all the connectionts from/to this component
        # TODO: Delete all the Ports from this component
        self._deleted_component = self.graph.unregister_component(self.component_id)

    def undo(self) -> Component:
        # TODO: Recreate all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self.graph.register_component(self._deleted_component)
        return self._deleted_component
