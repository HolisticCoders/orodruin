# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin.commands import ConnectPorts, CreateComponent, CreatePort
from orodruin.core import Component, Graph, Port, PortDirection, Scene
from orodruin.exceptions import (
    ConnectionOnSameComponentError,
    ConnectionToDifferentDirectionError,
    ConnectionToSameDirectionError,
    OutOfScopeConnectionError,
    PortAlreadyConnectedError,
)


def test_connect_port_init(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    ConnectPorts(scene, scene.root_graph(), port_a, port_b)
    ConnectPorts(scene, scene.root_graph(), port_a.uuid(), port_b.uuid())
    ConnectPorts(scene, scene.root_graph(), port_a, port_b, True)


def test_connect_port_do_undo_redo(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    assert not scene.connections()
    assert not scene.root_graph().connections()

    command = ConnectPorts(scene, scene.root_graph(), port_a, port_b)
    command.do()

    assert scene.connections()
    assert scene.root_graph().connections()

    # command.undo()

    # assert not scene.connections()
    # assert not scene.root_graph().connections()

    # command.redo()

    # assert scene.connections()
    # assert scene.root_graph().connections()


def test_connect_port_same_component_error(scene: Scene) -> None:
    component = CreateComponent(scene, "component").do()

    port_a = CreatePort(scene, component, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(scene, component, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionOnSameComponentError):
        command.do()


def test_connect_port_same_direction_error(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_a, port_b)

    with pytest.raises(ConnectionToSameDirectionError):
        command.do()


def test_connect_port_already_connected_error(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_a, port_b)
    command.do()

    with pytest.raises(PortAlreadyConnectedError):
        command.do()


def test_connect_port_force(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_a, port_b, force=True)
    command.do()
    command.do()


def test_connect_port_out_of_scope_error(scene: Scene) -> None:
    # Test with components being both root components.
    root_component = CreateComponent(scene, "root").do()
    component_a = CreateComponent(
        scene, "component_a", graph=root_component.graph()
    ).do()

    port_root = CreatePort(
        scene, root_component, "port_root", PortDirection.output, int
    ).do()
    port_a = CreatePort(scene, component_a, "port_a", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_root, port_a, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()

    # Test with components with different parents.
    component_b = CreateComponent(scene, "component_b", graph=component_a.graph()).do()
    component_c = CreateComponent(scene, "component_c", graph=component_b.graph()).do()

    port_b = CreatePort(scene, component_b, "port_b", PortDirection.output, int).do()
    port_c = CreatePort(scene, component_c, "port_c", PortDirection.input, int).do()

    command = ConnectPorts(scene, scene.root_graph(), port_b, port_c, force=True)
    with pytest.raises(OutOfScopeConnectionError):
        command.do()


def test_connect_port_different_direction_error(scene: Scene) -> None:
    parent = CreateComponent(scene, "parent").do()

    child = CreateComponent(scene, "child", graph=parent.graph()).do()

    port_parent = CreatePort(
        scene,
        parent,
        "port_parent",
        PortDirection.input,
        int,
    ).do()
    port_child = CreatePort(scene, child, "port_child", PortDirection.output, int).do()

    command = ConnectPorts(scene, parent.graph(), port_child, port_parent, True)
    with pytest.raises(ConnectionToDifferentDirectionError):
        command.do()
