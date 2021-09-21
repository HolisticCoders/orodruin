from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID, uuid4

from .connection import Connection
from .port import Port
from .signal import Signal

if TYPE_CHECKING:
    from .component import Component

logger = logging.getLogger(__name__)


@dataclass
class Graph:
    """Orodruin's Graph Class.

    A graph organizes components, ports, and connections between them.
    """

    _parent_component: Optional[Component] = None

    _uuid: UUID = field(default_factory=uuid4)

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

    def uuid(self) -> UUID:
        """UUID of this component."""
        return self._uuid

    def components(self) -> List[Component]:
        """Return the components registered to this graph."""
        return list(self._components.values())

    def component_from_uuid(self, uuid: UUID) -> Optional[Component]:
        """Find a component from its uuid."""
        return self._components.get(uuid)

    def ports(self) -> List[Port]:
        """Return the ports registered to this graph."""
        return list(self._ports.values())

    def port_from_uuid(self, uuid: UUID) -> Optional[Port]:
        """Find a port from its uuid."""
        return self._ports.get(uuid)

    def connections(self) -> List[Connection]:
        """Return the connections registered to this graph."""
        return list(self._connections.values())

    def connection_from_uuid(self, uuid: UUID) -> Optional[Connection]:
        """Find a connection from its uuid."""
        return self._connections.get(uuid)

    def parent_component(self) -> Optional[Component]:
        """Return this graph parent component."""
        return self._parent_component

    def register_component(self, component: Component) -> None:
        """Register an existing component to this graph."""
        self._components[component.uuid()] = component
        self.component_registered.emit(component)
        logger.debug("Registered component %s", component.uuid())

    def unregister_component(self, uuid: UUID) -> Component:
        """Remove a registered component from this graph."""
        component = self._components.pop(uuid)
        self.component_unregistered.emit(component)
        logger.debug("Unregistered component %s", uuid)
        return component

    def register_port(self, port: Port) -> None:
        """Register an existing port to this graph."""
        self._ports[port.uuid()] = port
        self.port_registered.emit(port)
        logger.debug("Registered port %s", port.uuid())

    def unregister_port(self, uuid: UUID) -> Port:
        """Remove a registered port from this graph."""
        port = self._ports.pop(uuid)
        self.port_unregistered.emit(port)
        logger.debug("Unregistered port %s", uuid)
        return port

    def register_connection(self, connection: Connection) -> None:
        """Register an existing connection to this graph."""
        self._connections[connection.uuid()] = connection
        self.connection_registered.emit(connection)
        logger.debug("Registered connection %s", connection.uuid())

    def unregister_connection(self, uuid: UUID) -> Connection:
        """Remove a registered connection from this graph."""
        connection = self._connections.pop(uuid)
        self.connection_unregistered.emit(connection)
        logger.debug("Unregistered connection %s", uuid)
        return connection
