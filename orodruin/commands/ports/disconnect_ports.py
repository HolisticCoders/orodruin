from dataclasses import dataclass, field
from typing import Optional

from orodruin.core import Connection, Port, State
from orodruin.core.graph import Graph, GraphLike
from orodruin.core.port.port import PortLike
from orodruin.core.utils import find_connection

from ..command import Command


@dataclass
class DisconnectPorts(Command):
    """Connect two ports of the same graph."""

    state: State
    graph: GraphLike
    source: PortLike
    target: PortLike

    _source: Port = field(init=False)
    _target: Port = field(init=False)
    _graph: Graph = field(init=False)
    _deleted_connection: Optional[Connection] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._source = self.state.port_from_portlike(self.source)
        self._target = self.state.port_from_portlike(self.target)
        self._graph = self.state.graph_from_graphlike(self.graph)

    def do(self) -> None:
        """Disconnect the source port from the target port."""
        self._deleted_connection = find_connection(
            self._graph,
            self._source,
            self._target,
        )
        if self._deleted_connection:
            self._graph.unregister_connection(self._deleted_connection)
            self.state.delete_connection(self._deleted_connection)

    def undo(self) -> None:
        raise NotImplementedError
