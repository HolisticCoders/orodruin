# pylint: disable = protected-access
"""GraphManager handles graph modifications and and ensures a valid state."""
from typing import TYPE_CHECKING, Set, Union

if TYPE_CHECKING:
    from .component import Component  # pylint: disable = cyclic-import
    from .port import Port  # pylint: disable = cyclic-import
    from .port_collection import (
        PortCollection,  # pylint: disable = cyclic-import
    )


class PortAlreadyConnectedError(ConnectionError):
    """Port Already Connected Error."""


class ConnectionOnSameComponenentError(ConnectionError):
    """Both ports about to be connected are on the same component."""


class PortNotConnectedError(ConnectionError):
    """Port Not Connected Error."""


class ComponentDoesNotExistError(ValueError):
    """Given component doesn't exist."""


class GraphManager:
    """GraphManager handles graph modifications and and ensures a valid state."""

    _components: Set["Component"] = set()

    @classmethod
    def register_component(cls, component: "Component") -> None:
        """Register a new component."""
        cls._components.add(component)

    @classmethod
    def clear_registered_components(cls):
        """Clear all registered components."""
        cls._components = set()

    @classmethod
    def components(cls):
        """All registered Component instances."""
        return cls._components

    @classmethod
    def component_from_path(cls, path: str) -> "Component":
        """Return an existing Component from the given path."""
        for instance in cls._components:
            if path == str(instance.path()):
                return instance
        raise ComponentDoesNotExistError(f"Component with path {path} does not exist")

    @staticmethod
    def port_from_path(component: "Component", port_path: str):
        """Get a port from the given path, relative to the component."""
        if port_path.startswith("."):
            port = component.port(port_path.strip("."))
        else:
            component_name, port_name = port_path.split(".")
            sub_component = next(
                (c for c in component.components() if c.name() == component_name), None
            )
            port = sub_component.port(port_name)

        return port

    @staticmethod
    def connect_ports(
        source: "Port", target: Union["Port", "PortCollection"], force: bool = False
    ):
        """
        Connect the source port to the target port.
        Raises:
            ConnectionOnSameComponenentError: when trying to connect on another port of
                the same Component
            PortAlreadyConnectedError: when connecting to an already connected port
                and the force argument is False
        """
        if target.component() is source.component():
            raise ConnectionOnSameComponenentError(
                f"{source.name()} and {target.name()} can't be connected because "
                f"they both are on the same component '{source._component.name()}'"
            )

        if source.type().name != target.type().name:
            raise TypeError(
                "Can't connect two ports of different types. "
                f"{source.name()}<{source._type.name}> to "
                f"{target.name()}<{target.type().name}>"
            )

        from .port import Port  # pylint: disable = import-outside-toplevel
        from .port_collection import (  # pylint: disable = import-outside-toplevel
            PortCollection,
        )

        if isinstance(target, Port):
            if target.source() and not force:
                raise PortAlreadyConnectedError(
                    f"port {target.name()} is already connected to "
                    f"{target.source().name()}, "
                    "use `force=True` to connect regardless."
                )

            if target.source() and force:
                GraphManager.disconnect_ports(target.source(), target)

        elif isinstance(target, PortCollection):
            target.add_port()
            target = target[-1]

        target._source = source
        source._targets.append(target)

    @staticmethod
    def disconnect_ports(source: "Port", target: "Port"):
        """Disconnect the two given ports."""
        if target not in source._targets:
            return
        source._targets.remove(target)
        target._source = None

    @staticmethod
    def sync_port_sizes(port: "PortCollection"):
        """Sync all the follower ports of the given port."""
        component = port.component()
        for synced_port in component._synced_ports.get(port, []):
            synced_port.add_port()
