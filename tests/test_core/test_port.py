# pylint: disable = missing-module-docstring, missing-function-docstring

import pytest

from orodruin.core import Component, Port, PortDirection
from orodruin.core.pathed_object import PathedObject


def test_port_issubclass_pathed_object() -> None:
    assert issubclass(Port, PathedObject)


def test_implements_port() -> None:
    assert issubclass(Port, Port)


def test_init_port() -> None:
    component = Component("component")
    port = Port("port", PortDirection.input, int, component)
    assert port.name() == "port"


def test_set_port_name() -> None:
    component = Component("component")
    port = Port("my_port", PortDirection.input, int, component)
    component.register_port(port)
    port = component.port("my_port")
    assert port.name() == "my_port"

    port.set_name("other_name")
    assert port.name() == "other_name"


def test_set_port_value(port: Port) -> None:
    port.set(1)
    assert port.get() == 1


def test_set_port_wrong_value_type(port: Port) -> None:
    with pytest.raises(TypeError):
        port.set("string")
