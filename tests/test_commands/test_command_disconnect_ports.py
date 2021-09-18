# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

from orodruin.commands import ConnectPorts, DisconnectPorts
from orodruin.core import Component, Port, PortDirection


def test_disconnect_port_init(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    DisconnectPorts(root.graph(), port_a, port_b)


def test_connect_port_do_undo_redo(
    root: Component, create_port: Callable[..., Port]
) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    component_a.set_parent_graph(root.graph())
    component_b.set_parent_graph(root.graph())

    port_a = create_port(component_a, "port_a", PortDirection.output)
    port_b = create_port(component_b, "port_b")

    ConnectPorts(root.graph(), port_a, port_b).do()

    command = DisconnectPorts(root.graph(), port_a, port_b)

    assert root.graph().connections()

    command.do()

    assert not root.graph().connections()

    command.undo()

    assert root.graph().connections()

    command.redo()

    assert not root.graph().connections()
