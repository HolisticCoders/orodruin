from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from ..component import Component
from ..graph import Graph
from .command import Command


@dataclass
class CreateComponent(Command):

    _graph: Graph
    _name: str
    _type: Optional[str] = None
    _created_component: Component = field(init=False)

    def do(self) -> None:
        component = Component(
            _name=self._name,
            _parent_graph=self._graph,
        )
        if self._type:
            component._type = self._type

        self._graph.register_component(component)
        self._created_component = component

    def undo(self) -> None:
        # TODO: Delete all the connectionts from/to this component
        # TODO: Delete all the Ports from this component
        self._graph.unregister_component(self._created_component.uuid())

    def redo(self) -> None:
        # TODO: Delete all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self._graph.register_component(self._created_component)


@dataclass
class DeleteComponent(Command):

    _graph: Graph
    _component_id: UUID

    _deleted_component: Component = field(init=False)

    def do(self) -> None:
        # TODO: Delete all the connectionts from/to this component
        # TODO: Delete all the Ports from this component
        self._deleted_component = self._graph.unregister_component(self._component_id)

    def undo(self) -> None:
        # TODO: Recreate all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self._graph.register_component(self._deleted_component)
