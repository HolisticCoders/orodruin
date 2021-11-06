from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attr

from orodruin.core.utils import find_connection

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, GraphLike, Port, PortLike, State


@attr.s
class DisconnectPorts(Command):
    """Connect two ports of the same graph."""

    state: State = attr.ib()
    graph: GraphLike = attr.ib()
    source: PortLike = attr.ib()
    target: PortLike = attr.ib()

    _source: Port = attr.ib(init=False)
    _target: Port = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)
    _deleted_connection: Optional[Connection] = attr.ib(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        self._source = self.state.get_port(self.source)
        self._target = self.state.get_port(self.target)
        self._graph = self.state.get_graph(self.graph)

    def do(self) -> None:
        """Disconnect the source port from the target port."""
        self._deleted_connection = find_connection(
            self._graph,
            self._source,
            self._target,
        )
        if self._deleted_connection:
            self._graph.unregister_connection(self._deleted_connection)
            self._source.unregister_downstream_connection(self._deleted_connection)
            self._target.unregister_upstream_connection(self._deleted_connection)
            self.state.delete_connection(self._deleted_connection)

        self._notify_downstream_ports(self._target)

    def undo(self) -> None:
        raise NotImplementedError

    def _notify_downstream_ports(self, port: Port) -> None:
        """Recursively notify the downstream ports that a connection was deleted."""
        port.upstream_connection_deleted.emit(port)
        for connection in port.connections(source=False, target=True):
            self._notify_downstream_ports(connection.target())
