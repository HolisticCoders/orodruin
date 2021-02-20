# pylint: disable = missing-module-docstring, missing-function-docstring, pointless-statement
import pytest

from orodruin.component import Component
from orodruin.port import Port
from orodruin.port_collection import PortCollection


def test_init_port():
    component = Component("component")
    port = PortCollection("port", Port.Direction.input, Port.Type.int, component)
    assert port.name() == "port"


def test_create_port_collection():
    component = Component("component")

    assert len(component.ports()) == 0

    component.add_port_collection(
        "my_port_collection",
        Port.Direction.input,
        Port.Type.int,
    )

    assert isinstance(component.my_port_collection, PortCollection)

    assert len(component.ports()) == 1


def test_access_sub_port():
    component = Component("component")
    component.add_port_collection(
        "my_multi_port",
        Port.Direction.input,
        Port.Type.int,
        size=1,
    )

    component.my_multi_port[0]


def test_access_nonexisting_sub_port():
    component = Component("component")
    component.add_port_collection("my_multi_port", Port.Direction.input, Port.Type.int)

    with pytest.raises(IndexError):
        component.my_multi_port[0]


def test_sync_ports():
    component = Component("component")
    component.add_port_collection("input", Port.Direction.input, Port.Type.int)
    component.add_port_collection("output", Port.Direction.input, Port.Type.int)

    component.sync_port_sizes(component.input, component.output)

    component.input.add_port()

    assert len(component.output.ports()) == 1
