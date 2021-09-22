# pylint: disable = missing-module-docstring, missing-function-docstring

import pytest

from orodruin.core import Port, PortDirection, Scene
from orodruin.core.pathed_object import PathedObject


def test_port_issubclass_pathed_object() -> None:
    assert issubclass(Port, PathedObject)


def test_implements_port() -> None:
    assert issubclass(Port, Port)


def test_init_port(scene: Scene) -> None:
    component = scene.create_component("component")
    port = scene.create_port("port", PortDirection.input, int, component.uuid())
    component.register_port(port)
    assert port.name() == "port"


def test_set_port_name(scene: Scene) -> None:
    component = scene.create_component("component")
    port = scene.create_port("port", PortDirection.input, int, component.uuid())
    component.register_port(port)

    assert port.name() == "port"

    port.set_name("new_name")

    assert port.name() == "new_name"

    port.set_name("other_name")
    assert port.name() == "other_name"


def test_set_port_value(scene: Scene) -> None:
    component = scene.create_component("component")
    port = scene.create_port("port", PortDirection.input, int, component.uuid())
    component.register_port(port)

    port.set(1)

    assert port.get() == 1


def test_set_port_wrong_value_type(scene: Scene) -> None:

    component = scene.create_component("component")
    port = scene.create_port("port", PortDirection.input, int, component.uuid())
    component.register_port(port)

    with pytest.raises(TypeError):
        port.set("string")  # type: ignore
