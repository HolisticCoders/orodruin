# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin.commands import ConnectPorts, CreateNode, CreatePort
from orodruin.core import Node, Graph, Port, PortDirection, State
from orodruin.exceptions import (
    ConnectionOnSameNodeError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)


def test_connect_port_init(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

    ConnectPorts(state, state.root_graph(), port_a, port_b)
    ConnectPorts(state, state.root_graph(), port_a.uuid(), port_b.uuid())
    ConnectPorts(state, state.root_graph(), port_a, port_b, True)


def test_connect_port_do_undo_redo(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

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


def test_connect_port_same_node_error(state: State) -> None:
    node = CreateNode(state, "node").do()

    port_a = CreatePort(state, node, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, node, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionOnSameNodeError):
        command.do()


def test_connect_port_same_direction_error(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionToSameDirectionError):
        command.do()


def test_connect_port_already_connected_error(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b)
    command.do()

    with pytest.raises(PortAlreadyConnectedError):
        command.do()


def test_connect_port_force(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_a, port_b, force=True)
    command.do()
    command.do()


def test_connect_port_out_of_scope_error(state: State) -> None:
    # Test with nodes being both root nodes.
    root_node = CreateNode(state, "root").do()
    node_a = CreateNode(state, "node_a", graph=root_node.graph()).do()

    port_root = CreatePort(
        state, root_node, "port_root", PortDirection.output, int
    ).do()
    port_a = CreatePort(state, node_a, "port_a", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_root, port_a, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with nodes with different parents.
    node_b = CreateNode(state, "node_b", graph=node_a.graph()).do()
    node_c = CreateNode(state, "node_c", graph=node_b.graph()).do()

    port_b = CreatePort(state, node_b, "port_b", PortDirection.output, int).do()
    port_c = CreatePort(state, node_c, "port_c", PortDirection.input, int).do()

    command = ConnectPorts(state, state.root_graph(), port_b, port_c, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()


def test_connect_port_different_direction_error(state: State) -> None:
    parent = CreateNode(state, "parent").do()

    child = CreateNode(state, "child", graph=parent.graph()).do()

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
