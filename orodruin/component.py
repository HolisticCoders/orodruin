from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Dict, List, Optional, Type
from uuid import uuid4

from .graph_manager import GraphManager
from .port import MultiPort, Port, SinglePort

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

    name: str
    _type: str
    library: Optional["Library"] = None
    _parent: Optional["Component"] = None

    _single_ports: List[SinglePort] = field(default_factory=list)
    _multi_ports: List[MultiPort] = field(default_factory=list)
    _synced_ports: Dict[str, MultiPort] = field(default_factory=dict)

    _components: List["Component"] = field(default_factory=list)

    @classmethod
    def new(
        cls,
        name: str,
        component_type: Optional[str] = None,
        library: Optional["Library"] = None,
        parent: Optional["Component"] = None,
    ) -> "Component":
        """Create a new component."""

        if component_type is None:
            component_type = str(uuid4())

        component = cls(name, component_type, library, parent)
        GraphManager.register_component(component)
        return component

    @property
    def type(self) -> str:
        """Type of the Component."""
        return self._type

    @property
    def ports(self) -> List[Port]:
        """List of the Component's Ports."""
        return self._single_ports + self._multi_ports

    @property
    def components(self):
        """Sub-components of the component."""
        return self._components

    @property
    def parent(self):
        """Parent of the component."""
        return self._parent

    @parent.setter
    def parent(self, other: "Component"):
        """Set the parent of the component."""
        if other is self:
            raise ParentToSelfError(f"Cannot parent {self.name} to itself")

        self._parent = other
        if self not in other.components:
            # TODO: refactor private member access
            other._components.append(self)  # pylint: disable= protected-access

    def __getattr__(self, name: str) -> Port:
        """Get the Ports of this Component if the Python attribut doesn't exist."""
        for port in self.ports:
            if port.name == name:
                return port

        raise NameError(f"Component {self.name} has no port named {name}")

    def port(self, name: str) -> Port:
        """Get a Port of this node from the its name."""

        return getattr(self, name)

    def add_port(
        self,
        name: str,
        direction: Port.Direction,
        port_type: Type,
    ) -> None:
        """Add a `SinglePort` to this Component."""
        port = SinglePort.new(name, direction, port_type, self)
        self._single_ports.append(port)

    def add_multi_port(
        self,
        name: str,
        direction: Port.Direction,
        port_type: Type,
        size: int = 0,
    ) -> None:
        """Add a `PortCollection` to this Component."""
        port = MultiPort.new(name, direction, port_type, size, self)
        self._multi_ports.append(port)

    def sync_port_sizes(self, master: MultiPort, slave: MultiPort):
        """Register Ports that needs their sizes synced.

        The follower port will be synced with the main's.
        """
        slaves: List[MultiPort] = self._synced_ports.get(master.name, [])

        if slave not in slaves:
            slaves.append(slave)
            self._synced_ports[master.name] = slaves

    @property
    def path(self) -> PurePosixPath:
        """Absolute Path of the Component."""
        if not self.parent:
            path = PurePosixPath(f"/{self.name}")
        else:
            path = self.parent.path.joinpath(f"{self.name}")

        return path

    def relative_path(self, relative_to: "Component") -> PurePosixPath:
        """Path of the Component relative to another one."""
        return self.path.relative_to(relative_to.path)
