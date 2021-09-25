"""Delete Port command."""
from dataclasses import dataclass, field

from orodruin.core import Component, Graph, Port, PortLike, State

from ..command import Command


@dataclass
class DeletePort(Command):
    """Delete Port command."""

    state: State
    port: PortLike

    _port: Port = field(init=False)
    _graph: Graph = field(init=False)
    _component: Component = field(init=False)

    def __post_init__(self) -> None:
        self._port = self.state.port_from_portlike(self.port)
        self._graph = self._port.graph()
        self._component = self._port.component()

    def do(self) -> None:
        # TODO: Delete all the connections from/to this component
        self._component.unregister_port(self.port)
        self._graph.unregister_port(self.port)
        self.state.delete_port(self.port)

    def undo(self) -> None:
        raise NotImplementedError
