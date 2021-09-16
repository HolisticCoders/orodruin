from dataclasses import dataclass, field
from typing import Optional

from ...connection import Connection
from ...graph import Graph
from ...port import Port
from ...utils import find_connection
from ..command import Command


@dataclass
class DisconnectPorts(Command):
    """Connect two ports of the same graph."""

    graph: Graph
    source: Port
    target: Port

    _deleted_connection: Optional[Connection] = field(init=False, default=None)

    def do(self) -> None:
        """Disconnect the source port from the target port."""
        self._deleted_connection = find_connection(self.graph, self.source, self.target)
        if self._deleted_connection:
            self.graph.unregister_connection(self._deleted_connection.uuid())

    def undo(self) -> None:
        if self._deleted_connection:
            self.graph.register_connection(self._deleted_connection)

    def redo(self) -> None:
        if self._deleted_connection:
            self.graph.unregister_connection(self._deleted_connection.uuid())
