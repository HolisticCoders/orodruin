from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Type
from uuid import uuid4

from orodruin.signal import Signal

from .graph_manager import GraphManager
from .port import MultiPort, Port, PortDirection, SinglePort

if TYPE_CHECKING:
    from .library import Library  # pylint: disable = cyclic-import


class ComponentError(Exception):
    """Generic Component Error"""


class ParentToSelfError(ComponentError):
    """Component parented to itself."""


class ComponentDoesNotExistError(ComponentError):
    """Component does not exist."""


@dataclass
class Component:
    """Orodruin's Component Class.

    A component can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Components as a subgraph
    """

    _name: str
    _type: str
    library: Optional[Library] = None
    _parent: Optional[Component] = None

    _ports: List[Port] = field(default_factory=list)
    _synced_ports: Dict[str, List[MultiPort]] = field(default_factory=dict)

    _components: List[Component] = field(default_factory=list)

    # Signals
    name_changed: Signal = field(default_factory=Signal)
    component_added: Signal = field(default_factory=Signal)
    port_added: Signal = field(default_factory=Signal)

    @classmethod
    def new(
        cls,
        name: str,
        component_type: Optional[str] = None,
        library: Optional[Library] = None,
        parent: Optional[Component] = None,
    ) -> Component:
        """Create a new component."""

        if component_type is None:
            component_type = str(uuid4())

        component = cls(name, component_type, library, parent)
        GraphManager.register_component(component)
        return component

    def type(self) -> str:
        """Type of the Component."""
        return self._type

    def ports(self) -> Sequence[Port]:
        """List of the Component's Ports."""
        return self._ports

    def components(self) -> List[Component]:
        """Sub-components of the component."""
        return self._components

    def parent(self) -> Optional[Component]:
        """Parent of the component."""
        return self._parent

    def set_parent(self, other: Component) -> None:
        """Set the parent of the component."""
        if other is self:
            raise ParentToSelfError(f"Cannot parent {self.name} to itself")

        self._parent = other
        other.add_child(self)

    def add_child(self, child: Component) -> None:
        """Parent the `component` under this component."""
        if child not in self._components:
            self._components.append(child)
        self.component_added.emit(child)

    def __getattr__(self, name: str) -> Port:
        """Get the Ports of this Component if the Python attribut doesn't exist."""
        for port in self.ports():
            if port.name() == name:
                return port

        raise NameError(f"Component {self.name()} has no port named {name}")

    def port(self, name: str) -> Port:
        """Get a Port of this node from the its name."""

        return getattr(self, name)

    def add_port(
        self,
        name: str,
        direction: PortDirection,
        port_type: Type,
    ) -> None:
        """Add a `SinglePort` to this Component."""
        port = SinglePort.new(name, direction, port_type, self)
        self._ports.append(port)
        self.port_added.emit(port, len(self._ports))

    def add_multi_port(
        self,
        name: str,
        direction: PortDirection,
        port_type: Type,
        size: int = 0,
    ) -> None:
        """Add a `PortCollection` to this Component."""
        port = MultiPort.new(name, direction, port_type, self, size)
        self._ports.append(port)

    def sync_port_sizes(self, master: MultiPort, slave: MultiPort) -> None:
        """Register Ports that needs their sizes synced.

        The follower port will be synced with the main's.
        """
        slaves = self._synced_ports.get(master.name(), [])

        if slave not in slaves:
            slaves.append(slave)
            self._synced_ports[master.name()] = slaves

    def name(self) -> str:
        """Name of the Component."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the Component."""
        self._name = name
        self.name_changed.emit(name)

    def path(self) -> PurePosixPath:
        """Absolute Path of the Component."""
        parent = self.parent()
        if parent:
            path = parent.path() / self.name()
        else:
            path = PurePosixPath(f"/{self.name()}")

        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Component relative to another one."""
        return self.path().relative_to(relative_to.path())
