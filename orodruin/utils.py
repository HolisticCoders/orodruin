from typing import Optional

from .component import Component
from .connection import Connection
from .graph import Graph
from .port import Port


class ComponentDoesNotExistError(ValueError):
    """Given component doesn't exist."""


def find_connection(graph: Graph, source: Port, target: Port) -> Optional[Connection]:
    """Find the connection between two ports of a graph."""
    for connection in graph.connections():
        if connection.source() != source:
            continue
        elif connection.target() != target:
            continue
        return connection
    return None


# def component_from_path(graph: Graph, path: str) -> Component:
#     """Return an existing Component from the given path."""
#     for instance in cls._components:
#         if path == str(instance.path()):
#             return instance
#     raise ComponentDoesNotExistError(f"Component with path {path} does not exist")


# def port_from_path(component: Component, port_path: str) -> Optional[Port]:
#     """Get a port from the given path, relative to the component."""
#     if port_path.startswith("."):
#         port = component.port(port_path.strip("."))
#     else:
#         component_name, port_name = port_path.split(".")
#         sub_component = next(
#             (c for c in component.components() if c.name() == component_name), None
#         )
#         if not sub_component:
#             raise ValueError(f"no port {port_path} found relative to {component}")
#         port = sub_component.port(port_name)

#     return port
