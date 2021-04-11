# pylint: disable = missing-module-docstring, missing-function-docstring, pointless-statement
import pytest

from orodruin.component import Component
from orodruin.port import MultiPort, Port


def test_init_port():
    component = Component.new("component")

    component.add_multi_port("my_port", Port.Direction.input, int)

    assert component.my_port.name == "my_port"


def test_create_multi_port():
    component = Component.new("component")

    assert len(component.ports) == 0

    component.add_multi_port(
        "my_multi_port",
        Port.Direction.input,
        int,
    )

    assert isinstance(component.my_multi_port, MultiPort)

    assert len(component.ports) == 1


def test_access_sub_port():
    component = Component.new("component")
    component.add_multi_port(
        "my_multi_port",
        Port.Direction.input,
        int,
        size=1,
    )

    component.my_multi_port[0]


def test_access_nonexisting_sub_port():
    component = Component.new("component")
    component.add_multi_port("my_multi_port", Port.Direction.input, int)

    with pytest.raises(IndexError):
        component.my_multi_port[0]


def test_sync_ports():
    component = Component.new("component")
    component.add_multi_port("input", Port.Direction.input, int)
    component.add_multi_port("output", Port.Direction.input, int)

    component.sync_port_sizes(component.input, component.output)

    component.input.add_port()

    assert len(component.output.ports) == 1
