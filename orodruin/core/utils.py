import re
from typing import Optional

from .connection import Connection
from .graph import Graph
from .node import Node
from .port import Port


def get_unique_node_name(graph: Graph, name: str) -> str:
    """Return a valid unique node name inside of the given graph."""
    name_pattern = re.compile(r"^(?P<basename>.*?)(?P<index>\d*)?$")

    for node in graph.nodes():
        if node.name() == name:

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

            new_name = f"{basename}{index}"

            return get_unique_node_name(graph, new_name)

    return name


def get_unique_port_name(node: Node, name: str) -> str:
    """Return a valid unique node name inside of the given graph."""
    name_pattern = re.compile(r"^(?P<basename>.*?)(?P<index>\d*)?$")

    for port in node.ports():
        if port.name() == name:

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

            new_name = f"{basename}{index}"

            return get_unique_port_name(node, new_name)

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


def get_most_upstream_port(port: Port) -> Port:
    """Recursively get the most upstream port connected to the given port."""
    connections = port.connections(source=True, target=False)
    if connections:
        return get_most_upstream_port(connections[0].source())
    return port


def port_from_path(parent_node: Node, port_path: str) -> Optional[Port]:
    """Get a port from the given path, relative to the node."""
    if port_path.startswith("."):
        port = parent_node.port(port_path.strip("."))
    else:
        node_name, port_name = port_path.split(".")

        sub_node = None
        for _sub_node in parent_node.graph().nodes():
            if node_name == _sub_node.name():
                sub_node = _sub_node
                break

        if sub_node is None:
            return None

        try:
            port = sub_node.port(port_name)
        except NameError:
            return None

    return port
