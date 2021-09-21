# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin.commands import ConnectPorts
from orodruin.core import Component, Graph, Port, PortDirection
from orodruin.exceptions import (
    ConnectionOnSameComponentError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)


def test_connect_port_init(root_graph: Graph, create_port: Callable[..., Port]) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    ConnectPorts(root_graph, port_a, port_b)


def test_connect_port_do_undo_redo(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root_graph)
    component_b.set_parent_graph(root_graph)

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    assert not root_graph.connections()

    command = ConnectPorts(root_graph, port_a, port_b)
    command.do()

    assert root_graph.connections()

    command.undo()

    assert not root_graph.connections()

    command.redo()

    assert root_graph.connections()


def test_connect_port_same_component_error(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    component = Component("component_a")

    port_a = create_port(component, "port_a")
    port_b = create_port(component, "port_b")

    component.set_parent_graph(root_graph)

    command = ConnectPorts(root_graph, port_a, port_b)

    with pytest.raises(ConnectionOnSameComponentError):
        command.do()


def test_connect_port_same_direction_error(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root_graph)
    component_b.set_parent_graph(root_graph)

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root_graph, port_a, port_b)

    with pytest.raises(ConnectionToSameDirectionError):
        command.do()


def test_connect_port_already_connected_error(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root_graph)
    component_b.set_parent_graph(root_graph)

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root_graph, port_a, port_b)
    command.do()

    with pytest.raises(PortAlreadyConnectedError):
        command.do()


def test_connect_port_force(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root_graph)
    component_b.set_parent_graph(root_graph)

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root_graph, port_a, port_b, True)
    command.do()
    command.do()


def test_connect_port_out_of_scope_error(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    # Test with components being both root components.
    root_component = Component("root")
    component_a = Component("component")
    component_a.set_parent_graph(root_component.graph())

    port_root = create_port(root_component, "port_root", PortDirection.output)
    port_a = create_port(component_a, "port_a")

    command = ConnectPorts(root_graph, port_root, port_a, True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_b = Component("component_b")
    component_b.set_parent_graph(root_graph)
    component_c = Component("component_c")
    component_c.set_parent_graph(component_b.graph())

    port_b = create_port(component_b, "port_b", PortDirection.output)
    port_c = create_port(component_c, "port_c")

    command = ConnectPorts(root_graph, port_b, port_c, True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_d = Component("component_d")
    component_d.set_parent_graph(root_graph)
    component_e = Component("component_e")
    component_e.set_parent_graph(component_d.graph())

    port_d = create_port(component_d, "port_d")
    port_e = create_port(component_e, "port_e")

    command = ConnectPorts(component_d.graph(), port_d, port_e, True)
    command.do()


def test_connect_port_different_direction_error(
    root_graph: Graph, create_port: Callable[..., Port]
) -> None:
    parent = Component("parent")
    parent.set_parent_graph(root_graph)

    child = Component("child")
    child.set_parent_graph(parent.graph())

    port_parent = create_port(parent, "port_parent")
    port_child = create_port(child, "port_child", PortDirection.output)

    command = ConnectPorts(parent.graph(), port_child, port_parent, True)
    with pytest.raises(ConnectionToDifferentDirectionError):
        command.do()
