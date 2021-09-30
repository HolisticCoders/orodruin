# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.core import PortDirection, State


def test_connection_source(state: State) -> None:
    node_a = state.create_node("node_a")
    node_b = state.create_node("node_b")

    port_a = state.create_port(
        "port_a", PortDirection.input, int, node_a, state.root_graph()
    )
    port_b = state.create_port(
        "port_b", PortDirection.input, int, node_b, state.root_graph()
    )

    node_a.register_port(port_a)
    node_b.register_port(port_b)

    connection = state.create_connection(
        state.root_graph(), port_a.uuid(), port_b.uuid()
    )

    assert connection.source() == port_a
    assert connection.target() == port_b
