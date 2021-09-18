"""Create Component command."""
from dataclasses import dataclass, field
from typing import Optional

from orodruin.core import Component, Graph, Library
from orodruin.core.utils import get_unique_name

from ..command import Command


@dataclass
class CreateComponent(Command):
    """Create Component command."""

    graph: Graph
    name: str
    type: Optional[str] = None
    library: Optional[Library] = None

    _created_component: Component = field(init=False)

    def do(self) -> Component:
        unique_name = get_unique_name(self.graph, self.name)
        component = Component(
            _name=unique_name,
            _parent_graph=self.graph,
        )
        if self.type:
            component.set_type(self.type)

        self.graph.register_component(component)
        self._created_component = component

        return self._created_component

    def undo(self) -> None:
        # TODO: Delete all the connections from/to this component
        # TODO: Delete all the Ports from this component
        self.graph.unregister_component(self._created_component.uuid())

    def redo(self) -> Component:
        # TODO: Delete all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self.graph.register_component(self._created_component)
        return self._created_component
