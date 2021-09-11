# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Generator

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager, PortAlreadyConnectedError
from orodruin.pathed_object import PathedObject
from orodruin.port import Port, PortDirection


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_port_issubclass_pathedobject() -> None:
    assert issubclass(Port, PathedObject)


def test_implements_port() -> None:
    assert issubclass(Port, Port)


def test_init_port() -> None:
    component = Component("component")
    port = Port("port", PortDirection.input, int, component, 0)
    assert port.name() == "port"


def test_set_port_name() -> None:
    component = Component("component")
    component.register_port("my_port", PortDirection.input, int)
    port = component.port("my_port")
    assert port.name() == "my_port"

    port.set_name("other_name")
    assert port.name() == "other_name"


def test_connect_ports() -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.register_port("port_a", PortDirection.output, int)
    component_b.register_port("port_b", PortDirection.input, int)

    assert len(component_a.port_a.targets()) == 0
    assert component_b.port_b.source() is None

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.targets()) == 1

    assert component_a.port_a.targets()[0] is component_b.port_b
    assert component_b.port_b.source() is component_a.port_a


def test_connect_already_connected_ports() -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.register_port("port_a", PortDirection.output, int)
    component_b.register_port("port_b", PortDirection.input, int)

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports() -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.register_port("port_a", PortDirection.output, int)
    component_b.register_port("port_b", PortDirection.input, int)

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_connect_different_type_ports() -> None:
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.register_port("output", PortDirection.output, bool)
    component_b.register_port("input", PortDirection.input, int)

    with pytest.raises(TypeError):
        component_a.output.connect(component_b.input)


def test_set_port_value() -> None:
    component = Component("component")
    component.register_port("my_port", PortDirection.input, int)

    component.my_port.set(1)
    assert component.my_port.get() == 1


def test_set_port_wrong_value_type() -> None:
    component = Component("component")
    component.register_port("my_port", PortDirection.input, str)

    with pytest.raises(TypeError):
        component.my_port.set(1)


def test_get_connected_port_value() -> None:
    component_a = Component("component")
    component_a.register_port("output", PortDirection.output, int)

    component_b = Component("component")
    component_b.register_port("input", PortDirection.input, int)

    component_a.output.connect(component_b.input)

    component_a.output.set(42)

    assert component_b.input.get() == 42
