# pylint: disable = too-many-instance-attributes
"""Orodruin's Component Class.

A component can be seen as both a node and a graph,
it has `Ports` to receive and pass Data through the graph
and can contain other Components as a subgraph
"""
from pathlib import PurePosixPath
from typing import List, Optional, Union
from uuid import UUID, uuid4

from .graph_manager import GraphManager
from .port import Port
from .port_collection import PortCollection


class ComponentError(Exception):
    """Generic Component Error"""


class ParentToSelfError(ComponentError):
    """Component parented to itself."""


class ComponentDoesNotExistError(ComponentError):
    """Component does not exist."""


class Component:
    """Orodruin's Component Class.

    A component can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Components as a subgraph
    """

    def __init__(self, name: str) -> None:
        self._name: str = name

        GraphManager.register_component(self)

        self._library = None
        self._type = uuid4()

        self._ports: List[Port] = []
        self._port_collections: List[PortCollection] = []
        self._synced_ports: List[PortCollection] = {}

        self._components: List[Component] = []
        self._parent: Optional[Component] = None

    def __getattr__(self, name: str) -> Optional[Union[Port, PortCollection]]:
        """Get the Ports of this Component if the Python attribut doesn't exist."""
        for port in self._ports + self._port_collections:
            if port.name() == name:
                return port

        return None

    def port(self, name) -> Port:
        """Get a Port of this node from the its name."""
        return getattr(self, name)

    def build(self) -> None:
        """Build the inner Graph of this Component.

        This method should be overriden for any Component
        that needs a direct implementation in each DCC
        """

    def publish(self) -> None:
        """Cleans up the Component to be ready for Animation."""

    def add_port(self, name: str, direction: Port.Direction, port_type: Port.Type):
        """Add a `Port` to this Component."""
        port = Port(name, direction, port_type, self)
        self._ports.append(port)

    def add_port_collection(
        self,
        name: str,
        direction: Port.Direction,
        port_type: Port.Type,
        size: int = 0,
    ):
        """Add a `PortCollection` to this Component."""
        port = PortCollection(name, direction, port_type, self, size)
        self._port_collections.append(port)

    def name(self) -> str:
        """Name of the Component."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the component."""
        self._name = name

    def type(self) -> str:
        """Type of the Component."""

        return self._type

    def set_type(self, component_type: str):
        """Set the type of the component."""

        try:
            component_type = UUID(component_type)
        except ValueError:
            pass

        self._type = component_type

    def library(self) -> Optional[str]:
        """Type of the Component."""
        return self._library

    def set_library(self, component_library: Optional[str]):
        """Set the library of the component."""
        self._library = component_library

    def path(self, relative_to: Optional["Component"] = None) -> PurePosixPath:
        """The Path of this Component, absolute or relative."""
        if self._parent is None:
            path = PurePosixPath(f"/{self._name}")
        else:
            path = self._parent.path().joinpath(f"{self._name}")

        if relative_to:
            path = path.relative_to(relative_to.path())

        return path

    def ports(self):
        """List of the Component's Ports."""
        return self._ports + self._port_collections

    def sequence_ports(self):
        """List of the Component's Ports."""
        return self._sequence_ports

    def components(self):
        """Sub-components of the component."""
        return self._components

    def parent(self):
        """Parent of the component."""
        return self._parent

    def set_parent(self, other: "Component"):
        """Set the parent of the component."""
        if other is self:
            raise ParentToSelfError(f"Cannot parent {self._name} to itself")

        self._parent = other
        if self not in other.components():
            # TODO: refactor private member access
            other._components.append(self)  # pylint: disable= protected-access

    def sync_port_sizes(self, main: PortCollection, follower: PortCollection):
        """Register Ports that needs their sizes synced.

        The follower port will be synced with the main's.
        """
        slaves = self._synced_ports.get(main, [])

        if follower not in slaves:
            slaves.append(follower)
            self._synced_ports[main] = slaves
