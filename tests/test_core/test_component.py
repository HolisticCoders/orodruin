# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath

import pytest

from orodruin.core import Component, Port, PortDirection, Scene
from orodruin.core.pathed_object import PathedObject


def test_implements_pathed_object() -> None:
    issubclass(Component, PathedObject)


def test_init_component(scene: Scene) -> None:
    assert len(scene.components()) == 0

    component = scene.create_component("component")

    assert len(scene.components()) == 1
    assert component.name() == "component"


def test_add_ports(scene: Scene) -> None:

    component = scene.create_component("component")

    assert len(component.ports()) == 0

    input1 = scene.create_port("input1", PortDirection.input, int, component.uuid())
    input2 = scene.create_port("input2", PortDirection.input, int, component.uuid())
    output = scene.create_port("output", PortDirection.input, int, component.uuid())

    assert len(scene.ports()) == 3

    component.register_port(input1)
    component.register_port(input2)
    component.register_port(output)

    assert len(component.ports()) == 3


def test_set_name(scene: Scene) -> None:
    component = scene.create_component("original_name")

    assert component.name() == "original_name"

    component.set_name("new_name")

    assert component.name() == "new_name"


def test_path_root_component(scene: Scene) -> None:
    component = scene.create_component("root")
    assert component.path() == PurePosixPath("/root")


def test_path_nested_component(scene: Scene) -> None:
    root_component = scene.create_component("root")
    child_a = scene.create_component("child_a")
    child_b = scene.create_component("child_b")

    child_a.set_parent_graph(root_component.graph().uuid())
    child_b.set_parent_graph(child_a.graph().uuid())

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative(scene: Scene) -> None:
    root_component = scene.create_component("root")
    child_a = scene.create_component("child_a")
    child_b = scene.create_component("child_b")

    child_a.set_parent_graph(root_component.graph().uuid())
    child_b.set_parent_graph(child_a.graph().uuid())

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port(scene: Scene) -> None:
    component = scene.create_component("component")
    port = scene.create_port("input1", PortDirection.input, int, component.uuid())
    component.register_port(port)
    assert isinstance(component.port("input1"), Port)


def test_access_innexisting_port(scene: Scene) -> None:
    component = scene.create_component("component")
    with pytest.raises(NameError):
        component.port("this_is_not_a_port")
