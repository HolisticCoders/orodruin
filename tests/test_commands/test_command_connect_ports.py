# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin.commands import ConnectPorts, CreateComponent, CreatePort
from orodruin.core import Component, Graph, Port, PortDirection, State
from orodruin.exceptions import (
    ConnectionOnSameComponentError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)


def test_connect_port_init(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    ConnectPorts(state, state.root_graph(), port_a, port_b)
    ConnectPorts(state, state.root_graph(), port_a.uuid(), port_b.uuid())
    ConnectPorts(state, state.root_graph(), port_a, port_b, True)


def test_connect_port_do_undo_redo(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    assert not state.connections()
    assert not state.root_graph().connections()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)
    command.do()

    assert state.connections()
    assert state.root_graph().connections()

    # command.undo()

    # assert not state.connections()
    # assert not state.root_graph().connections()

    # command.redo()

    # assert state.connections()
    # assert state.root_graph().connections()


def test_connect_port_same_component_error(state: State) -> None:
    component = CreateComponent(state, "component").do()

    port_a = CreatePort(state, component, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, component, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionOnSameComponentError):
        command.do()


def test_connect_port_same_direction_error(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionToSameDirectionError):
        command.do()


def test_connect_port_already_connected_error(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)
    command.do()

    with pytest.raises(PortAlreadyConnectedError):
        command.do()


def test_connect_port_force(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b, force=True)
    command.do()
    command.do()


def test_connect_port_out_of_scope_error(state: State) -> None:
    # Test with components being both root components.
    root_component = CreateComponent(state, "root").do()
    component_a = CreateComponent(
        state, "component_a", graph=root_component.graph()
    ).do()

    port_root = CreatePort(
        state, root_component, "port_root", PortDirection.output, int
    ).do()
    port_a = CreatePort(state, component_a, "port_a", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_root, port_a, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_b = CreateComponent(state, "component_b", graph=component_a.graph()).do()
    component_c = CreateComponent(state, "component_c", graph=component_b.graph()).do()

    port_b = CreatePort(state, component_b, "port_b", PortDirection.output, int).do()
    port_c = CreatePort(state, component_c, "port_c", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_b, port_c, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()


def test_connect_port_different_direction_error(state: State) -> None:
    parent = CreateComponent(state, "parent").do()

    child = CreateComponent(state, "child", graph=parent.graph()).do()

    port_parent = CreatePort(
        state,
        parent,
        "port_parent",
        PortDirection.input,
        int,
    ).do()
    port_child = CreatePort(state, child, "port_child", PortDirection.output, int).do()

    command = ConnectPorts(state, parent.graph(), port_child, port_parent, True)
    with pytest.raises(ConnectionToDifferentDirectionError):
        command.do()
