# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin import Component, Port, PortDirection
from orodruin.commands.connections import (
    ConnectionOnSameComponentError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    ConnectPorts,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)


def test_connect_port_init(root: Component, create_port: Callable[..., Port]) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    ConnectPorts(root.graph(), port_a, port_b)


def test_connect_port_do_undo_redo(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root.graph())
    component_b.set_parent_graph(root.graph())

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    assert not root.graph().connections()

    command = ConnectPorts(root.graph(), port_a, port_b)
    command.do()

    assert root.graph().connections()

    command.undo()

    assert not root.graph().connections()

    command.redo()

    assert root.graph().connections()


def test_connect_port_same_component_error(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component = Component("component_a")

    port_a = create_port(component, "port_a")
    port_b = create_port(component, "port_b")

    component.set_parent_graph(root.graph())

    command = ConnectPorts(root.graph(), port_a, port_b)

    with pytest.raises(ConnectionOnSameComponentError):
        command.do()


def test_connect_port_same_direction_error(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root.graph())
    component_b.set_parent_graph(root.graph())

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root.graph(), port_a, port_b)

    with pytest.raises(ConnectionToSameDirectionError):
        command.do()


def test_connect_port_already_connected_error(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root.graph())
    component_b.set_parent_graph(root.graph())

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root.graph(), port_a, port_b)
    command.do()

    with pytest.raises(PortAlreadyConnectedError):
        command.do()


def test_connect_port_force(root: Component, create_port: Callable[..., Port]) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root.graph())
    component_b.set_parent_graph(root.graph())

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    command = ConnectPorts(root.graph(), port_a, port_b, True)
    command.do()
    command.do()


def test_connect_port_out_of_scope_error(
    root: Component, create_port: Callable[..., Port]
) -> None:
    # Test with components being both root components.
    component_a = Component("component")

    port_root = create_port(root, "port_root", PortDirection.output)
    port_a = create_port(component_a, "port_a")

    command = ConnectPorts(root.graph(), port_root, port_a, True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_b = Component("component_b")
    component_b.set_parent_graph(root.graph())
    component_c = Component("component_c")
    component_c.set_parent_graph(component_b.graph())

    port_b = create_port(component_b, "port_b", PortDirection.output)
    port_c = create_port(component_c, "port_c")

    command = ConnectPorts(root.graph(), port_b, port_c, True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_d = Component("component_d")
    component_d.set_parent_graph(root.graph())
    component_e = Component("component_e")
    component_e.set_parent_graph(component_d.graph())

    port_d = create_port(component_d, "port_d")
    port_e = create_port(component_e, "port_e")

    command = ConnectPorts(component_d.graph(), port_d, port_e, True)
    command.do()


def test_connect_port_different_direction_error(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component = Component("component")
    component.set_parent_graph(root.graph())

    port_root = create_port(root, "port_root")
    port = create_port(component, "port_a", PortDirection.output)

    command = ConnectPorts(root.graph(), port_root, port, True)
    with pytest.raises(ConnectionToDifferentDirectionError):
        command.do()
