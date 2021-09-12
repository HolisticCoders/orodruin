from dataclasses import dataclass
from typing import Optional

from ..connection import Connection
from ..graph import Graph
from ..port import Port
from ..utils import find_connection
from .command import Command


class PortAlreadyConnectedError(ConnectionError):
    """Port Already Connected Error."""


class ConnectionOnSameComponentError(ConnectionError):
    """Both ports about to be connected are on the same component."""


class OutOfScopeConnectionError(ConnectionError):
    """Connection from two components not in the same scope."""


class ConnectionToSameDirectionError(ConnectionError):
    """Two ports of the same direction and scope are being connected together."""


class ConnectionToDifferentDirectionError(ConnectionError):
    """Two ports of the component and its parent direction are being connected together
    while they have the same direction.
    """


@dataclass
class ConnectPorts(Command):
    """Connect two ports of the same graph."""

    _graph: Graph
    _source: Port
    _target: Port
    _force: bool = False
    _deleted_connection: Optional[Connection] = None
    _created_connection: Optional[Connection] = None

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
            self._graph
            in [
                self._source.component().graph(),
                self._source.component().parent_graph(),
            ]
            and self._graph
            in [
                self._target.component().graph(),
                self._target.component().parent_graph(),
            ]
        ):
            raise OutOfScopeConnectionError(
                f"port {self._source.name()} and{self._target.name()} "
                f"don't exist in the same scope"
            )

        if self._target.component() is self._source.component():
            raise ConnectionOnSameComponentError(
                f"{self._source.name()} and {self._target.name()} "
                "can't be connected because they both are on the same component "
                f"'{self._source.component().name()}'"
            )

        if self._source.type() is not self._target.type():
            raise TypeError(
                "Can't connect two ports of different types. "
                f"{self._source.name()}<{self._source.type().__name__}> to "
                f"{self._target.name()}<{self._target.type().__name__}>"
            )

        same_scope_connection = (
            self._source.component().parent_graph() is not None
            and self._target.component().parent_graph() is not None
            and (
                self._source.component().parent_graph()
                == self._target.component().parent_graph()
            )
        )
        connection_with_parent = (
            self._source.component().parent_component() == self._target.component()
            or self._source.component() == self._target.component().parent_component()
        )
        if same_scope_connection:
            if self._source.direction() == self._target.direction():
                raise ConnectionToSameDirectionError(
                    f"port {self._source.name()} and{self._target.name()} "
                    f"are of the same direction. "
                    f"Connection in the same scope can only go from input to output."
                )
        elif connection_with_parent:
            if self._source.direction() != self._target.direction():
                raise ConnectionToDifferentDirectionError(
                    f"port {self._source.name()} and{self._target.name()} "
                    f"are of different directions. "
                    f"connection from or to the parent component "
                    "can only be of the same direction."
                )

        self._deleted_connection = find_connection(
            self._graph, self._source, self._target
        )
        if self._deleted_connection:
            if self._force:
                self._graph.unregister_connection(self._deleted_connection.uuid())
            else:
                raise PortAlreadyConnectedError(
                    f"port {self._target.name()} is already connected to "
                    f"{self._deleted_connection.source().name()}, "
                    "use `force=True` to connect regardless."
                )

        self._created_connection = Connection(self._source, self._target)
        self._graph.register_connection(self._created_connection)

        return self._created_connection

    def undo(self) -> None:
        if self._created_connection:
            self._graph.unregister_connection(self._created_connection.uuid())
        if self._deleted_connection:
            self._graph.register_connection(self._deleted_connection)

    def redo(self) -> None:
        if self._deleted_connection:
            self._graph.unregister_connection(self._deleted_connection.uuid())
        if self._created_connection:
            self._graph.register_connection(self._created_connection)

        return self._created_connection
