from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from .connection import Connection
from .port import Port
from .signal import Signal

if TYPE_CHECKING:
    from .component import Component


@dataclass
class Graph:
    """Orodruin's Graph Class.

    A graph organizes components, ports, and connections between them.
    """

    _parent_component: Component

    _components: Dict[UUID, Component] = field(default_factory=dict)
    _ports: Dict[UUID, Port] = field(default_factory=dict)
    _connections: Dict[UUID, Connection] = field(default_factory=dict)

    # Signals
    component_registered: Signal[Component] = field(default_factory=Signal)
    component_unregistered: Signal[Component] = field(default_factory=Signal)
    port_registered: Signal[Port] = field(default_factory=Signal)
    port_unregistered: Signal[Port] = field(default_factory=Signal)
    connection_registered: Signal[Connection] = field(default_factory=Signal)
    connection_unregistered: Signal[Connection] = field(default_factory=Signal)

    def components(self) -> Dict[UUID, Component]:
        """Return the components registered to this graph, mapped by UUID."""
        return self._components

    def ports(self) -> Dict[UUID, Port]:
        """Return the ports registered to this graph, mapped by UUID."""
        return self._ports

    def connections(self) -> Dict[UUID, Connection]:
        """Return the connections registered to this graph, mapped by UUID."""
        return self._connections

    def parent_component(self) -> Component:
        """Return this graph parent component."""
        return self._parent_component

    def register_component(self, component: Component) -> None:
        """Register an existing component to this graph."""
        self._components[component.uuid()] = component
        self.component_registered.emit(component)

    def unregister_component(self, uuid: UUID) -> Component:
        """Remove a registered component from this graph."""
        component = self._components.pop(uuid)
        self.component_unregistered.emit(component)
        return component

    def register_port(self, port: Port) -> None:
        """Register an existing port to this graph."""
        self._ports[port.uuid()] = port
        self.port_registered.emit(port)

    def unregister_port(self, uuid: UUID) -> Port:
        """Remove a registered port from this graph."""
        port = self._ports.pop(uuid)
        self.port_unregistered.emit(port)
        return port

    def register_connection(self, connection: Connection) -> None:
        """Register an existing connection to this graph."""
        self._connections[connection.uuid()] = connection
        self.connection_registered.emit(connection)

    def unregister_connection(self, uuid: UUID) -> Connection:
        """Remove a registered connection from this graph."""
        connection = self._connections.pop(uuid)
        self.connection_unregistered.emit(connection)
        return connection
