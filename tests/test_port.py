import pytest

from orodruin.port import (
    Port,
    PortAlreadyConnectedError,
    PortNotConnectedError,
    PortSide,
)
from orodruin.component import Component


def test_init_port():
    component = Component("component")
    port = Port("port", component)
    assert port.name() == "port"


def test_set_port_name():
    component = Component("component")
    port = Port("port", component)
    assert port.name() == "port"

    port.set_name("other name")
    assert port.name() == "other name"


def test_connect_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortSide.output)
    component_b.add_port("port_b", PortSide.input)

    assert len(component_a.port_a.connections()) == 0
    assert len(component_b.port_b.connections()) == 0

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.connections()) == 1
    assert len(component_b.port_b.connections()) == 1

    assert component_a.port_a.connections()[0] is component_b.port_b
    assert component_b.port_b.connections()[0] is component_a.port_a


def test_connect_already_connected_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortSide.output)
    component_b.add_port("port_b", PortSide.input)

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortSide.output)
    component_b.add_port("port_b", PortSide.input)

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_disconnect_non_connected_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortSide.output)
    component_b.add_port("port_b", PortSide.input)

    with pytest.raises(PortNotConnectedError):
        component_a.port_a.disconnect(component_b.port_b)
