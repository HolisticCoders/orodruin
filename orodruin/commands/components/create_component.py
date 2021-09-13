from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from ...component import Component
from ...graph import Graph
from ..command import Command


@dataclass
class CreateComponent(Command):

    _graph: Graph
    _name: str
    _type: Optional[str] = None
    _created_component: Component = field(init=False)

    def do(self) -> Component:
        component = Component(
            _name=self._name,
            _parent_graph=self._graph,
        )
        if self._type:
            component._type = self._type

        self._graph.register_component(component)
        self._created_component = component

        return self._created_component

    def undo(self) -> None:
        # TODO: Delete all the connectionts from/to this component
        # TODO: Delete all the Ports from this component
        self._graph.unregister_component(self._created_component.uuid())

    def redo(self) -> Component:
        # TODO: Delete all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self._graph.register_component(self._created_component)
        return self._created_component
