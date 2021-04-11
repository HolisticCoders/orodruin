# pylint: disable = missing-module-docstring, missing-function-docstring, pointless-statement
import pytest

from orodruin.component import Component
from orodruin.port import MultiPort, PortDirection


def test_init_port() -> None:
    component = Component.new("component")

    component.add_multi_port("my_port", PortDirection.input, int)

    assert component.my_port.name == "my_port"


def test_create_multi_port() -> None:
    component = Component.new("component")

    assert len(component.ports) == 0

    component.add_multi_port(
        "my_multi_port",
        PortDirection.input,
        int,
    )

    assert isinstance(component.my_multi_port, MultiPort)

    assert len(component.ports) == 1


def test_access_sub_port() -> None:
    component = Component.new("component")
    component.add_multi_port(
        "my_multi_port",
        PortDirection.input,
        int,
        size=1,
    )

    component.my_multi_port[0]


def test_access_nonexisting_sub_port() -> None:
    component = Component.new("component")
    component.add_multi_port("my_multi_port", PortDirection.input, int)

    with pytest.raises(IndexError):
        component.my_multi_port[0]


def test_sync_ports() -> None:
    component = Component.new("component")
    component.add_multi_port("input", PortDirection.input, int)
    component.add_multi_port("output", PortDirection.input, int)

    component.sync_port_sizes(component.input, component.output)

    component.input.add_port()

    assert len(component.output.ports) == 1
