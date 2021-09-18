from dataclasses import dataclass, field
from typing import List, Optional

from orodruin.core import Connection, Graph, Port
from orodruin.core.utils import list_connections
from orodruin.exceptions import (
    ConnectionOnSameComponentError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)

from ..command import Command


@dataclass
class ConnectPorts(Command):
    """Connect two ports of the same graph."""

    graph: Graph
    source: Port
    target: Port
    force: bool = False

    _deleted_connections: List[Connection] = field(default_factory=list)
    _created_connection: Optional[Connection] = field(init=False, default=None)

    def do(self) -> Connection:
        """Connect the source port to the target port.

        Raises:
            ConnectionOnSameComponentError: when trying to connect on another port of
                the same Component
            TypeError: when trying to connect ports of different types.
            ConnectionToSameDirectionError: when two ports of the same direction
                and scope are being connected together.
            ConnectionToDifferentDirectionError: when two ports of the component
                and its parent direction are being connected together while they
                have the same direction.
            OutOfScopeConnectionError: when trying to connect ports from
                different graphs.
            PortAlreadyConnectedError: when connecting to an already connected port
                and the force argument is False
        """
        if not (
            self.graph
            in [
                self.source.component().graph(),
                self.source.component().parent_graph(),
            ]
            and self.graph
            in [
                self.target.component().graph(),
                self.target.component().parent_graph(),
            ]
        ):
            raise OutOfScopeConnectionError(
                f"Port {self.source.name()} "
                f"cannot be connected to {self.target.name()}. "
                f"Ports don't exist in the same scope"
            )

        if self.target.component() is self.source.component():
            raise ConnectionOnSameComponentError(
                f"Port {self.source.name()} "
                f"cannot be connected to {self.target.name()}. "
                "Both ports exist on the same component."
            )

        try:
            self.target.type()(self.source.get())
        except TypeError as e:
            raise TypeError(
                f"Port {self.source.name()} "
                f"cannot be connected to {self.target.name()}. "
                f"Impossible to cast {self.source.type().__name__} to "
                f"{self.target.type().__name__}."
            ) from e

        same_scope_connection = (
            self.source.component().parent_graph() is not None
            and self.target.component().parent_graph() is not None
            and (
                self.source.component().parent_graph()
                == self.target.component().parent_graph()
            )
        )
        connection_with_parent = (
            self.source.component().parent_component() == self.target.component()
            or self.source.component() == self.target.component().parent_component()
        )
        if same_scope_connection:
            if self.source.direction() == self.target.direction():
                raise ConnectionToSameDirectionError(
                    f"Port {self.source.name()} "
                    f"cannot be connected to {self.target.name()}. "
                    f"Both ports are {self.source.direction()} ports."
                )
        elif connection_with_parent:
            if self.source.direction() != self.target.direction():
                raise ConnectionToDifferentDirectionError(
                    f"Port {self.source.name()} "
                    f"cannot be connected to {self.target.name()}. "
                    "Both ports are of different direction. "
                    "Connection with the parent component "
                    "can only be of the same direction."
                )

        self._deleted_connections = list_connections(self.graph, self.target)
        if self._deleted_connections:
            if self.force:
                for connection in self._deleted_connections:
                    self.graph.unregister_connection(connection.uuid())
            else:
                raise PortAlreadyConnectedError(
                    f"Port {self.source.name()} "
                    f"cannot be connected to {self.target.name()}. "
                    f"port {self.target.name()} is already connected "
                    "use `force=True` to connect regardless."
                )

        self._created_connection = Connection(self.source, self.target)
        self.graph.register_connection(self._created_connection)

        return self._created_connection

    def undo(self) -> None:
        if self._created_connection:
            self.graph.unregister_connection(self._created_connection.uuid())
        for connection in self._deleted_connections:
            self.graph.register_connection(connection)

    def redo(self) -> None:
        for connection in self._deleted_connections:
            self.graph.unregister_connection(connection.uuid())
        if self._created_connection:
            self.graph.register_connection(self._created_connection)
