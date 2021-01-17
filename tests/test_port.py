# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin.component import Component
from orodruin.port import Port, PortAlreadyConnectedError


def test_init_port(create_component: Callable[..., Component]):
    component = create_component("component")
    port = Port("port", component)
    assert port.name() == "port"


def test_set_port_name(create_component: Callable[..., Component]):
    component = create_component("component")
    port = Port("port", component)
    assert port.name() == "port"

    port.set_name("other name")
    assert port.name() == "other name"


def test_connect_ports(create_component: Callable[..., Component]):
    component_a = create_component("component_a")
    component_b = create_component("component_b")
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    assert len(component_a.port_a.targets()) == 0
    assert component_b.port_b.source() is None

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.targets()) == 1

    assert component_a.port_a.targets()[0] is component_b.port_b
    assert component_b.port_b.source() is component_a.port_a


def test_connect_already_connected_ports(create_component: Callable[..., Component]):
    component_a = create_component("component_a")
    component_b = create_component("component_b")
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports(create_component: Callable[..., Component]):
    component_a = create_component("component_a")
    component_b = create_component("component_b")
    component_a.add_port("port_a")
    component_b.add_port("port_b")

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_set_port_value(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port("port")

    component.port.set(1)
    assert component.port.get() == 1

    component.port.set("asdf")
    assert component.port.get() == "asdf"

    component.port.set(True)
    assert component.port.get()


def test_get_connected_port_value(create_component: Callable[..., Component]):
    component_a = create_component("component")
    component_a.add_port("output")

    component_b = create_component("component")
    component_b.add_port("input")

    component_a.output.connect(component_b.input)

    component_a.output.set(42)

    assert component_b.input.get() == 42
