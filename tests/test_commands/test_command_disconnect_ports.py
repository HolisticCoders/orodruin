# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import ConnectPorts, CreateComponent, CreatePort, DisconnectPorts
from orodruin.core import Component, PortDirection, State


def test_disconnect_port_init(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    DisconnectPorts(state, state.root_graph(), port_a, port_b)
    DisconnectPorts(state, state.root_graph(), port_a.uuid(), port_b.uuid())


def test_connect_port_do_undo_redo(state: State) -> None:
    component_a = CreateComponent(state, "component_a").do()
    component_b = CreateComponent(state, "component_b").do()

    port_a = CreatePort(state, component_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, component_b, "port_b", PortDirection.input, int).do()

    ConnectPorts(state, state.root_graph(), port_a, port_b).do()

    command = DisconnectPorts(state, state.root_graph(), port_a, port_b)

    assert state.connections()
    assert state.root_graph().connections()

    command.do()

    assert not state.connections()
    assert not state.root_graph().connections()

    # command.undo()

    # assert state.connections()
    # assert state.root_graph().connections()

    # command.redo()

    # assert not state.connections()
    # assert not state.root_graph().connections()
