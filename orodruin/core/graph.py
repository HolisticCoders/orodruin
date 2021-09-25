from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID, uuid4

from .signal import Signal

if TYPE_CHECKING:
    from .component import Component, ComponentLike
    from .connection import Connection, ConnectionLike
    from .port import Port, PortLike
    from .state import State

logger = logging.getLogger(__name__)


@dataclass
class Graph:
    """Orodruin's Graph Class.

    A graph organizes components, ports, and connections between them.
    """

    _state: State
    _parent_component_id: Optional[UUID] = None

    _uuid: UUID = field(default_factory=uuid4)

    _component_ids: List[UUID] = field(default_factory=list)
    _port_ids: List[UUID] = field(default_factory=list)
    _connections_ids: List[UUID] = field(default_factory=list)

    # Signals
    component_registered: Signal[Component] = field(default_factory=Signal)
    component_unregistered: Signal[Component] = field(default_factory=Signal)
    port_registered: Signal[Port] = field(default_factory=Signal)
    port_unregistered: Signal[Port] = field(default_factory=Signal)
    connection_registered: Signal[Connection] = field(default_factory=Signal)
    connection_unregistered: Signal[Connection] = field(default_factory=Signal)

    def state(self) -> State:
        """Return the state that owns this graph."""
        return self._state

    def uuid(self) -> UUID:
        """UUID of this component."""
        return self._uuid

    def components(self) -> List[Component]:
        """Return the components registered to this graph."""
        components = []

        for component_id in self._component_ids:
            component = self._state.component_from_componentlike(component_id)
            components.append(component)

        return components

    def ports(self) -> List[Port]:
        """Return the ports registered to this graph."""
        ports = []

        for port_id in self._port_ids:
            port = self._state.port_from_portlike(port_id)
            ports.append(port)

        return ports

    def connections(self) -> List[Connection]:
        """Return the connections registered to this graph."""
        connections = []

        for connection_id in self._connections_ids:
            connection = self._state.connection_from_connectionlike(connection_id)
            connections.append(connection)

        return connections

    def parent_component(self) -> Optional[Component]:
        """Return this graph parent component."""
        if self._parent_component_id:
            return self._state.component_from_componentlike(self._parent_component_id)
        return None

    def register_component(self, component: ComponentLike) -> None:
        """Register an existing component to this graph."""
        component = self._state.component_from_componentlike(component)

        self._component_ids.append(component.uuid())
        component.set_parent_graph(self.uuid())
        self.component_registered.emit(component)

        logger.debug(
            "Registered component %s to graph %s",
            component.path(),
            self.uuid(),
        )

    def unregister_component(self, component: ComponentLike) -> None:
        """Remove a registered component from this graph."""
        component = self._state.component_from_componentlike(component)

        self._component_ids.remove(component.uuid())
        component.set_parent_graph(None)
        self.component_unregistered.emit(component)

        logger.debug(
            "Unregistered component %s from graph %s",
            component.path(),
            self.uuid(),
        )

    def register_port(self, port: PortLike) -> None:
        """Register an existing port to this graph."""
        port = self._state.port_from_portlike(port)

        self._port_ids.append(port.uuid())
        self.port_registered.emit(port)

        logger.debug("Registered port %s to graph %s", port.path(), self.uuid())

    def unregister_port(self, port: PortLike) -> None:
        """Remove a registered port from this graph."""
        port = self._state.port_from_portlike(port)

        self._port_ids.remove(port.uuid())
        self.port_unregistered.emit(port)

        logger.debug("Unregistered port %s from graph %s", port.path(), self.uuid())

    def register_connection(self, connection: ConnectionLike) -> None:
        """Register an existing connection to this graph."""
        connection = self._state.connection_from_connectionlike(connection)

        self._connections_ids.append(connection.uuid())
        self.connection_registered.emit(connection)

        logger.debug(
            "Registered connection %s to graph %s",
            connection.uuid(),
            self.uuid(),
        )

    def unregister_connection(self, connection: ConnectionLike) -> None:
        """Remove a registered connection from this graph."""
        connection = self._state.connection_from_connectionlike(connection)

        self._connections_ids.remove(connection.uuid())
        self.connection_unregistered.emit(connection)

        logger.debug(
            "Unregistered connection %s from graph %s",
            connection.uuid(),
            self.uuid(),
        )


GraphLike = Union[Graph, UUID]

__all__ = [
    "Graph",
    "GraphLike",
]
