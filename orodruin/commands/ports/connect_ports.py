from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import attr

from orodruin.core.utils import list_connections
from orodruin.exceptions import (
    ConnectionOnSameNodeError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, GraphLike, Port, PortLike, State


@attr.s
class ConnectPorts(Command):
    """Connect two ports of the same graph."""

    state: State = attr.ib()
    graph: GraphLike = attr.ib()
    source: PortLike = attr.ib()
    target: PortLike = attr.ib()
    force: bool = attr.ib(default=False)

    _source: Port = attr.ib(init=False)
    _target: Port = attr.ib(init=False)
    _graph: Graph = attr.ib(init=False)
    _deleted_connections: List[Connection] = attr.ib(factory=list)
    _created_connection: Optional[Connection] = attr.ib(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        self._source = self.state.get_port(self.source)
        self._target = self.state.get_port(self.target)
        self._graph = self.state.get_graph(self.graph)

    def do(self) -> Connection:
        """Connect the source port to the target port.

        Raises:
            ConnectionOnSameNodeError: when trying to connect on another port of
                the same Node
            TypeError: when trying to connect ports of different types.
            ConnectionToSameDirectionError: when two ports of the same direction
                and scope are being connected together.
            ConnectionToDifferentDirectionError: when two ports of the node
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
                self._source.node().graph(),
                self._source.node().parent_graph(),
            ]
            and self._graph
            in [
                self._target.node().graph(),
                self._target.node().parent_graph(),
            ]
        ):
            raise OutOfScopeConnectionError(
                f"Port {self._source.name()} "
                f"cannot be connected to {self._target.name()}. "
                f"Ports don't exist in the same scope"
            )

        if self._target.node() is self._source.node():
            raise ConnectionOnSameNodeError(
                f"Port {self._source.name()} "
                f"cannot be connected to {self._target.name()}. "
                "Both ports exist on the same node."
            )

        try:
            self._target.type()(self._source.get())
        except TypeError as e:
            raise TypeError(
                f"Port {self._source.name()} "
                f"cannot be connected to {self._target.name()}. "
                f"Impossible to cast {self._source.type().__name__} to "
                f"{self._target.type().__name__}."
            ) from e

        same_scope_connection = (
            self._source.node().parent_graph() is not None
            and self._target.node().parent_graph() is not None
            and (
                self._source.node().parent_graph() == self._target.node().parent_graph()
            )
        )
        connection_with_parent = (
            self._source.node().parent_node() == self._target.node()
            or self._source.node() == self._target.node().parent_node()
        )
        if same_scope_connection:
            if self._source.direction() == self._target.direction():
                raise ConnectionToSameDirectionError(
                    f"Port {self._source.name()} "
                    f"cannot be connected to {self._target.name()}. "
                    f"Both ports are {self._source.direction()} ports."
                )
        elif connection_with_parent:
            if self._source.direction() != self._target.direction():
                raise ConnectionToDifferentDirectionError(
                    f"Port {self._source.name()} "
                    f"cannot be connected to {self._target.name()}. "
                    "Both ports are of different direction. "
                    "Connection with the parent node "
                    "can only be of the same direction."
                )

        self._deleted_connections = list_connections(self._graph, self._target)
        if self._deleted_connections:
            if self.force:
                for connection in self._deleted_connections:
                    self._graph.unregister_connection(connection.uuid())
            else:
                raise PortAlreadyConnectedError(
                    f"Port {self._source.name()} "
                    f"cannot be connected to {self._target.name()}. "
                    f"port {self._target.name()} is already connected "
                    "use `force=True` to connect regardless."
                )

        self._created_connection = self.state.create_connection(
            self._graph, self._source, self._target
        )
        self._graph.register_connection(self._created_connection)

        return self._created_connection

    def undo(self) -> None:
        raise NotImplementedError
