from dataclasses import dataclass, field
from typing import List, Optional

from orodruin.core import Connection, Graph, Port
from orodruin.core.graph import GraphLike
from orodruin.core.port.port import PortLike
from orodruin.core.scene import Scene
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

    scene: Scene
    graph: GraphLike
    source: PortLike
    target: PortLike
    force: bool = False

    _source: Port = field(init=False)
    _target: Port = field(init=False)
    _graph: Graph = field(init=False)
    _deleted_connections: List[Connection] = field(default_factory=list)
    _created_connection: Optional[Connection] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._source = self.scene.port_from_portlike(self.source)
        self._target = self.scene.port_from_portlike(self.target)
        self._graph = self.scene.graph_from_graphlike(self.graph)

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
                f"Port {self._source.name()} "
                f"cannot be connected to {self._target.name()}. "
                f"Ports don't exist in the same scope"
            )

        if self._target.component() is self._source.component():
            raise ConnectionOnSameComponentError(
                f"Port {self._source.name()} "
                f"cannot be connected to {self._target.name()}. "
                "Both ports exist on the same component."
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
                    "Connection with the parent component "
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

        self._created_connection = self.scene.create_connection(
            self._source, self._target
        )
        self._graph.register_connection(self._created_connection)

        return self._created_connection

    def undo(self) -> None:
        raise NotImplementedError
