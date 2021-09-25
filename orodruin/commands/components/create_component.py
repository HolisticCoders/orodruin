"""Create Component command."""
from dataclasses import dataclass, field
from typing import Optional

from orodruin.core import Component, Graph, Library
from orodruin.core.graph import GraphLike
from orodruin.core.state import State
from orodruin.core.utils import get_unique_name

from ..command import Command


@dataclass
class CreateComponent(Command):
    """Create Component command."""

    state: State
    name: str
    type: Optional[str] = None
    library: Optional[Library] = None
    graph: Optional[GraphLike] = None

    _graph: Graph = field(init=False)
    _created_component: Component = field(init=False)

    def __post_init__(self) -> None:
        if self.graph:
            self._graph = self.state.graph_from_graphlike(self.graph)
        else:
            self._graph = self.state.root_graph()

    def do(self) -> Component:
        unique_name = get_unique_name(self._graph, self.name)

        component = self.state.create_component(
            name=unique_name,
            parent_graph_id=self._graph.uuid(),
            library=self.library,
        )
        if self.type:
            component.set_type(self.type)

        self._graph.register_component(component)
        self._created_component = component

        return self._created_component

    def undo(self) -> None:
        raise NotImplementedError
