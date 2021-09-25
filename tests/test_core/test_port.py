# pylint: disable = missing-module-docstring, missing-function-docstring

import pytest

from orodruin.core import Port, PortDirection, State
from orodruin.core.pathed_object import PathedObject


def test_port_issubclass_pathed_object() -> None:
    assert issubclass(Port, PathedObject)


def test_implements_port() -> None:
    assert issubclass(Port, Port)


def test_init_port(state: State) -> None:
    node = state.create_node("node")
    port = state.create_port("port", PortDirection.input, int, node.uuid())
    node.register_port(port)
    assert port.name() == "port"


def test_set_port_name(state: State) -> None:
    node = state.create_node("node")
    port = state.create_port("port", PortDirection.input, int, node.uuid())
    node.register_port(port)

    assert port.name() == "port"

    port.set_name("new_name")

    assert port.name() == "new_name"

    port.set_name("other_name")
    assert port.name() == "other_name"


def test_set_port_value(state: State) -> None:
    node = state.create_node("node")
    port = state.create_port("port", PortDirection.input, int, node.uuid())
    node.register_port(port)

    port.set(1)

    assert port.get() == 1


def test_set_port_wrong_value_type(state: State) -> None:

    node = state.create_node("node")
    port = state.create_port("port", PortDirection.input, int, node.uuid())
    node.register_port(port)

    with pytest.raises(TypeError):
        port.set("string")  # type: ignore
