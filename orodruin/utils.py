from typing import List, Optional

from .component import Component
from .connection import Connection
from .graph import Graph
from .port import Port


class ComponentDoesNotExistError(ValueError):
    """Given component doesn't exist."""


class PortDoesNotExistError(ValueError):
    """Given component doesn't exist."""


def find_connection(graph: Graph, source: Port, target: Port) -> Optional[Connection]:
    """Find the connection between two ports of a graph."""
    for connection in graph.connections():
        if connection.source() != source:
            continue
        if connection.target() != target:
            continue
        return connection
    return None


def list_connections(graph, port: Port) -> List[Connection]:
    """Find all the connections connected to the given port."""
    connections = []
    for connection in graph.connections():
        if connection.source() is port or connection.target() is port:
            connections.append(connection)

    return connections


def port_from_path(component: Component, port_path: str) -> Optional[Port]:
    """Get a port from the given path, relative to the component."""
    if port_path.startswith("."):
        port = component.port(port_path.strip("."))
    else:
        component_name, port_name = port_path.split(".")

        sub_component = None
        for _sub_component in component.graph().components():
            if component_name == _sub_component.name():
                sub_component = _sub_component
                break

        if sub_component is None:
            return None

        try:
            port = sub_component.port(port_name)
        except NameError:
            return None

    return port
