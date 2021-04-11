# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Generator

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager, PortAlreadyConnectedError
from orodruin.port import Port, PortDirection, SinglePort


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_singleport_implements_port() -> None:
    component = Component.new("component")
    port = SinglePort("port", PortDirection.input, int, component, 0)

    assert isinstance(port, Port)


def test_init_port() -> None:
    component = Component.new("component")
    port = SinglePort("port", PortDirection.input, int, component, 0)
    assert port.name == "port"


def test_set_port_name() -> None:
    component = Component.new("component")
    component.add_port("my_port", PortDirection.input, int)
    port = component.port("my_port")
    assert port.name == "my_port"

    port.name = "other_name"
    assert port.name == "other_name"


def test_connect_ports() -> None:
    component_a = Component.new("component_a")
    component_b = Component.new("component_b")
    component_a.add_port("port_a", PortDirection.output, int)
    component_b.add_port("port_b", PortDirection.input, int)

    assert len(component_a.port_a.targets) == 0
    assert component_b.port_b.source is None

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.targets) == 1

    assert component_a.port_a.targets[0] is component_b.port_b
    assert component_b.port_b.source is component_a.port_a


def test_connect_already_connected_ports() -> None:
    component_a = Component.new("component_a")
    component_b = Component.new("component_b")
    component_a.add_port("port_a", PortDirection.output, int)
    component_b.add_port("port_b", PortDirection.input, int)

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports() -> None:
    component_a = Component.new("component_a")
    component_b = Component.new("component_b")
    component_a.add_port("port_a", PortDirection.output, int)
    component_b.add_port("port_b", PortDirection.input, int)

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_connect_different_type_ports() -> None:
    component_a = Component.new("component_a")
    component_b = Component.new("component_b")
    component_a.add_port("output", PortDirection.output, bool)
    component_b.add_port("input", PortDirection.input, int)

    with pytest.raises(TypeError):
        component_a.output.connect(component_b.input)


def test_set_port_value() -> None:
    component = Component.new("component")
    component.add_port("my_port", PortDirection.input, int)

    component.my_port.set(1)
    assert component.my_port.get() == 1


def test_set_port_wrong_value_type() -> None:
    component = Component.new("component")
    component.add_port("my_port", PortDirection.input, str)

    with pytest.raises(TypeError):
        component.my_port.set(1)


def test_get_connected_port_value() -> None:
    component_a = Component.new("component")
    component_a.add_port("output", PortDirection.output, int)

    component_b = Component.new("component")
    component_b.add_port("input", PortDirection.input, int)

    component_a.output.connect(component_b.input)

    component_a.output.set(42)

    assert component_b.input.get() == 42
