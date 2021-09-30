# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import ConnectPorts, CreateNode, CreatePort, DisconnectPorts
from orodruin.core import Node, PortDirection, State


def test_disconnect_port_init(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.input, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

    DisconnectPorts(state, state.root_graph(), port_a, port_b)
    DisconnectPorts(state, state.root_graph(), port_a.uuid(), port_b.uuid())


def test_connect_port_do_undo_redo(state: State) -> None:
    node_a = CreateNode(state, "node_a").do()
    node_b = CreateNode(state, "node_b").do()

    port_a = CreatePort(state, node_a, "port_a", PortDirection.output, int).do()
    port_b = CreatePort(state, node_b, "port_b", PortDirection.input, int).do()

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
