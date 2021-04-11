# pylint: disable = protected-access
"""GraphManager handles graph modifications and and ensures a valid state."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, TypeVar

if TYPE_CHECKING:
    from .component import Component  # pylint: disable = cyclic-import
    from .port import MultiPort, Port  # pylint: disable = cyclic-import

T = TypeVar("T")  # pylint: disable = invalid-name


class PortAlreadyConnectedError(ConnectionError):
    """Port Already Connected Error."""


class ConnectionOnSameComponenentError(ConnectionError):
    """Both ports about to be connected are on the same component."""


class OutOfScopeConnectionError(ConnectionError):
    """Connection from two components not in the same scope."""


class ConnectionToSameDirectionError(ConnectionError):
    """Two ports of the same direction and scope are being connected together."""


class ConnectionToDifferentDirectionError(ConnectionError):
    """Two ports of the component and its parent direction are being connected together
    while they have the same direction.
    """


class PortNotConnectedError(ConnectionError):
    """Port Not Connected Error."""


class ComponentDoesNotExistError(ValueError):
    """Given component doesn't exist."""


class GraphManager:
    """GraphManager handles graph modifications and and ensures a valid state."""

    _components: List[Component] = []

    @classmethod
    def register_component(cls, component: Component) -> None:
        """Register a new component."""
        if component not in cls._components:
            cls._components.append(component)

    @classmethod
    def clear_registered_components(cls) -> None:
        """Clear all registered components."""
        cls._components = []

    @classmethod
    def components(cls) -> List[Component]:
        """All registered Component instances."""
        return cls._components

    @classmethod
    def component_from_path(cls, path: str) -> Component:
        """Return an existing Component from the given path."""
        for instance in cls._components:
            if path == str(instance.path):
                return instance
        raise ComponentDoesNotExistError(f"Component with path {path} does not exist")

    @staticmethod
    def port_from_path(component: Component, port_path: str) -> Optional[Port]:
        """Get a port from the given path, relative to the component."""
        if port_path.startswith("."):
            port = component.port(port_path.strip("."))
        else:
            component_name, port_name = port_path.split(".")
            sub_component = next(
                (c for c in component.components if c.name == component_name), None
            )
            if not sub_component:
                raise ValueError(f"no port {port_path} found relative to {component}")
            port = sub_component.port(port_name)

        return port

    @staticmethod
    def connect_ports(
        source: Port,
        target: Port,
        force: bool = False,
    ) -> None:
        """
        Connect the source port to the target port.
        Raises:
            ConnectionOnSameComponenentError: when trying to connect on another port of
                the same Component
            PortAlreadyConnectedError: when connecting to an already connected port
                and the force argument is False
        """
        if target.component is source.component:
            raise ConnectionOnSameComponenentError(
                f"{source.name} and {target.name} can't be connected because "
                f"they both are on the same component '{source.component.name}'"
            )

        if source.type is not target.type:
            raise TypeError(
                "Can't connect two ports of different types. "
                f"{source.name}<{source.type.__name__}> to "
                f"{target.name}<{target.type.__name__}>"
            )

        same_scope_connection = source.component.parent == target.component.parent
        connection_with_parent = (
            source.component.parent == target.component
            or source.component == target.component.parent
        )
        if same_scope_connection:
            if source.direction == target.direction:
                raise ConnectionToSameDirectionError(
                    f"port {source.name} and{target.name} "
                    f"are of the same direction. "
                    f"Connection in the same scope can only go from input to output."
                )
        elif connection_with_parent:
            if source.direction != target.direction:
                raise ConnectionToDifferentDirectionError(
                    f"port {source.name} and{target.name} "
                    f"are of different directions. "
                    f"connection from or to the parent component "
                    "can only be of the same direction."
                )
        else:
            raise OutOfScopeConnectionError(
                f"port {source.name} and{target.name} " f"don't exist in the same scope"
            )

        from .port import (  # pylint: disable = import-outside-toplevel
            MultiPort,
            SinglePort,
        )

        if isinstance(target, SinglePort):
            if target.source and not force:
                raise PortAlreadyConnectedError(
                    f"port {target.name} is already connected to "
                    f"{target.source.name}, "
                    "use `force=True` to connect regardless."
                )

            if target.source and force:
                GraphManager.disconnect_ports(target.source, target)
        if isinstance(target, MultiPort):
            target.add_port()
            target = target[-1]

        target._source = source
        source._targets.append(target)

    @staticmethod
    def disconnect_ports(source: Port, target: Port) -> None:
        """Disconnect the two given ports."""
        if target not in source.targets:
            return

        source._targets.remove(target)
        target._source = None

    @staticmethod
    def sync_port_sizes(port: MultiPort) -> None:
        """Sync all the follower ports of the given port."""
        component = port.component
        for synced_port in component._synced_ports.get(port.name, []):
            synced_port.add_port()
