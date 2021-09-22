# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import ConnectPorts, CreateComponent, CreatePort, DisconnectPorts
from orodruin.core import Component, PortDirection, Scene


def test_disconnect_port_init(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    DisconnectPorts(scene, scene.root_graph(), port_a, port_b)
    DisconnectPorts(scene, scene.root_graph(), port_a.uuid(), port_b.uuid())


def test_connect_port_do_undo_redo(scene: Scene) -> None:
    component_a = CreateComponent(scene, "component_a").do()
    component_b = CreateComponent(scene, "component_b").do()

    port_a = CreatePort(scene, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(scene, component_b, "port_b", PortDirection.input, int).do()

    ConnectPorts(scene, scene.root_graph(), port_a, port_b).do()

    command = DisconnectPorts(scene, scene.root_graph(), port_a, port_b)

    assert scene.connections()
    assert scene.root_graph().connections()

    command.do()

    assert not scene.connections()
    assert not scene.root_graph().connections()

    # command.undo()

    # assert scene.connections()
    # assert scene.root_graph().connections()

    # command.redo()

    # assert not scene.connections()
    # assert not scene.root_graph().connections()
