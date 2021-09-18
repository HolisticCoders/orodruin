# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

from orodruin.core import Component, Connection, Port


def test_connection_source(create_port: Callable[..., Port]) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    connection = Connection(port_a, port_b)

    assert connection.source() == port_a


def test_connection_target(create_port: Callable[..., Port]) -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")

    port_a = create_port(component_a, "port_a")
    port_b = create_port(component_b, "port_b")

    connection = Connection(port_a, port_b)

    assert connection.target() == port_b
