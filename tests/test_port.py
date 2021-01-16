import pytest

from orodruin.component import Component
from orodruin.port import (
    Port,
    PortAlreadyConnectedError,
    PortNotConnectedError,
)


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
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    assert len(component_a.port_a.targets()) == 0
    assert component_b.port_b.source() is None

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.targets()) == 1

    assert component_a.port_a.targets()[0] is component_b.port_b
    assert component_b.port_b.source() is component_a.port_a


def test_connect_already_connected_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_set_port_value():
    component = Component("component")
    component.add_port("port")

    component.port.set(1)
    assert component.port.get() == 1

    component.port.set("asdf")
    assert component.port.get() == "asdf"

    component.port.set(True)
    assert component.port.get() == True


def test_get_connected_port_value():
    a = Component("component")
    a.add_port("output")

    b = Component("component")
    b.add_port("input")

    a.output.connect(b.input)

    a.output.set(42)

    assert b.input.get() == 42
