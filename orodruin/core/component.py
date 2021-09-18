from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID, uuid4

from .graph import Graph
from .port import Port
from .signal import Signal

if TYPE_CHECKING:
    from .library import Library  # pylint: disable = cyclic-import


@dataclass
class Component:
    """Orodruin's Component Class.

    A component can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Components as a subgraph
    """

    _name: str
    _type: str = field(default_factory=lambda: str(uuid4()))

    _library: Optional[Library] = None
    _parent_graph: Optional[Graph] = None
    _graph: Graph = field(init=False)

    _ports: Dict[UUID, Port] = field(default_factory=dict)

    _uuid: UUID = field(default_factory=uuid4)

    # Signals
    name_changed: Signal[str] = field(default_factory=Signal)
    port_registered: Signal[Port] = field(default_factory=Signal)
    port_unregistered: Signal[Port] = field(default_factory=Signal)

    def __post_init__(self) -> None:
        self._graph = Graph(self)

    def type(self) -> str:
        """Type of the Component."""
        return self._type

    def set_type(self, value: str) -> None:
        """Type of the Component."""
        self._type = value

    def ports(self) -> List[Port]:
        """List of the Component's Ports."""
        return list(self._ports.values())

    def uuid(self) -> UUID:
        """UUID of this component."""
        return self._uuid

    def library(self) -> Optional[Library]:
        """Return the library declaring this component."""
        return self._library

    def set_library(self, library: Library) -> None:
        """Set the library declaring this component."""
        self._library = library

    def parent_graph(self) -> Optional[Graph]:
        """Parent graph of the component."""
        return self._parent_graph

    def set_parent_graph(self, graph: Graph) -> None:
        """Set the parent graph of the component."""
        self._parent_graph = graph

    def graph(self) -> Graph:
        """Graph containing child components."""
        return self._graph

    def parent_component(self) -> Optional[Component]:
        """Parent component."""
        if not self._parent_graph:
            return None
        return self._parent_graph.parent_component()

    def __getattr__(self, name: str) -> Port:
        """Get the Ports of this Component if the Python attribute doesn't exist."""
        for port in self.ports():
            if port.name() == name:
                return port

        raise NameError(f"Component {self.name()} has no port named {name}")

    def port(self, name: str) -> Port:
        """Get a Port of this node from the its name."""
        return getattr(self, name)

    def register_port(self, port: Port) -> None:
        """Register an existing port to this component."""
        self._ports[port.uuid()] = port
        self.port_registered.emit(port)

    def unregister_port(self, uuid: UUID) -> Port:
        """Remove a registered port from this component."""
        port = self._ports.pop(uuid)
        self.port_unregistered.emit(port)
        return port

    def name(self) -> str:
        """Name of the Component."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the Component."""
        self._name = name
        self.name_changed.emit(name)

    def path(self) -> PurePosixPath:
        """Absolute Path of the Component."""
        parent = self.parent_component()
        if parent:
            path = parent.path() / self.name()
        else:
            path = PurePosixPath(f"/{self.name()}")

        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Component relative to another one."""
        return self.path().relative_to(relative_to.path())
