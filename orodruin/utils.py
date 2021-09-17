import re
from typing import List, Optional

from .component import Component
from .connection import Connection
from .graph import Graph
from .port import Port


class ComponentDoesNotExistError(ValueError):
    """Given component doesn't exist."""


class PortDoesNotExistError(ValueError):
    """Given component doesn't exist."""


def get_unique_name(graph: Graph, name: str) -> str:
    """Return a valid unique component name inside of the given graph."""
    name_pattern = re.compile(r"^(?P<basename>.*?)(?P<index>\d*)?$")

    for component in graph.components():
        if component.name() == name:

            match = name_pattern.match(name)
            if not match:
                raise NameError(f"{name} did not match regex pattern {name_pattern}")

            groups = match.groupdict()
            basename = groups["basename"]
            index_str = groups.get("index")

            if not index_str:
                index = 0
            else:
                index = int(index_str)
            index += 1

            name = f"{basename}{index}"

            get_unique_name(graph, name)
    return name


def find_connection(graph: Graph, source: Port, target: Port) -> Optional[Connection]:
    """Find the connection between two ports of a graph."""
    for connection in graph.connections():
        if connection.source() != source:
            continue
        if connection.target() != target:
            continue
        return connection
    return None


def list_connections(graph: Graph, port: Port) -> List[Connection]:
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
