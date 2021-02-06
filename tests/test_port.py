# pylint: disable = missing-module-docstring, missing-function-docstring
import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager, PortAlreadyConnectedError
from orodruin.port import Port, PortType


@pytest.fixture(autouse=True)
def clear_registered_components():

    yield
    GraphManager.clear_registered_components()


def test_init_port():
    component = Component("component")
    port = Port("port", PortType.int, component)
    assert port.name() == "port"


def test_set_port_name():
    component = Component("component")
    port = Port("port", PortType.int, component)
    assert port.name() == "port"

    port.set_name("other name")
    assert port.name() == "other name"


def test_connect_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortType.int)
    component_b.add_port("port_b", PortType.int)

    assert len(component_a.port_a.targets()) == 0
    assert component_b.port_b.source() is None

    component_a.port_a.connect(component_b.port_b)

    assert len(component_a.port_a.targets()) == 1

    assert component_a.port_a.targets()[0] is component_b.port_b
    assert component_b.port_b.source() is component_a.port_a


def test_connect_already_connected_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortType.int)
    component_b.add_port("port_b", PortType.int)

    component_a.port_a.connect(component_b.port_b)
    with pytest.raises(PortAlreadyConnectedError):
        component_a.port_a.connect(component_b.port_b)


def test_disconnect_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("port_a", PortType.int)
    component_b.add_port("port_b", PortType.int)

    component_a.port_a.connect(component_b.port_b)
    component_a.port_a.disconnect(component_b.port_b)


def test_connect_different_type_ports():
    component_a = Component("component_a")
    component_b = Component("component_b")
    component_a.add_port("output", PortType.bool)
    component_b.add_port("input", PortType.int)

    with pytest.raises(TypeError):
        component_a.output.connect(component_b.input)


def test_set_port_value():
    component = Component("component")
    component.add_port("port", PortType.int)

    component.port.set(1)
    assert component.port.get() == 1


def test_set_port_wrong_value_type():
    component = Component("component")
    component.add_port("port", PortType.string)

    with pytest.raises(TypeError):
        component.port.set(1)


def test_get_connected_port_value():
    component_a = Component("component")
    component_a.add_port("output", PortType.int)

    component_b = Component("component")
    component_b.add_port("input", PortType.int)

    component_a.output.connect(component_b.input)

    component_a.output.set(42)

    assert component_b.input.get() == 42
