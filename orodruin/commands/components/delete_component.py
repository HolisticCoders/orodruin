"""Delete Component command."""
from dataclasses import dataclass, field

from orodruin.core import Component, ComponentLike, Graph, GraphLike, Scene
from orodruin.core.utils import list_connections

from ..command import Command
from ..ports import DeletePort, DisconnectPorts


@dataclass
class DeleteComponent(Command):
    """Delete Component command."""

    scene: Scene
    component: ComponentLike

    _component: Component = field(init=False)
    _graph: Graph = field(init=False)

    def __post_init__(self) -> None:
        self._component = self.scene.component_from_componentlike(self.component)
        self._graph = self._component.parent_graph()

    def do(self) -> None:
        for port in self._component.ports():
            for connection in list_connections(self._graph, port):
                DisconnectPorts(
                    self._graph,
                    connection.source(),
                    connection.target(),
                ).do()

            DeletePort(self.scene, port).do()

        self._graph.unregister_component(self._component)
        self.scene.delete_component(self._component)

    def undo(self) -> None:
        raise NotImplementedError
