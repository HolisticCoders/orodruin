# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.core import PortDirection, Scene


def test_connection_source(scene: Scene) -> None:
    component_a = scene.create_component("component_a")
    component_b = scene.create_component("component_b")

    port_a = scene.create_port("port_a", PortDirection.input, int, component_a.uuid())
    port_b = scene.create_port("port_b", PortDirection.input, int, component_b.uuid())

    component_a.register_port(port_a)
    component_b.register_port(port_b)

    connection = scene.create_connection(port_a.uuid(), port_b.uuid())

    assert connection.source() == port_a
    assert connection.target() == port_b
