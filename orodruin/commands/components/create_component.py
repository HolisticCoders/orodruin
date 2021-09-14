from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from orodruin.library import Library

from ...component import Component
from ...graph import Graph
from ..command import Command


@dataclass
class CreateComponent(Command):

    graph: Graph
    name: str
    type: Optional[str] = None
    library: Optional[Library] = None

    created_component: Component = field(init=False)

    def do(self) -> Component:
        component = Component(
            _name=self.name,
            _parent_graph=self.graph,
        )
        if self.type:
            component._type = self.type

        self.graph.register_component(component)
        self.created_component = component

        return self.created_component

    def undo(self) -> None:
        # TODO: Delete all the connectionts from/to this component
        # TODO: Delete all the Ports from this component
        self.graph.unregister_component(self.created_component.uuid())

    def redo(self) -> Component:
        # TODO: Delete all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self.graph.register_component(self.created_component)
        return self.created_component
