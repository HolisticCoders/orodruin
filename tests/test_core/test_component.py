# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath

import pytest

from orodruin.core import Component, Port, PortDirection, State
from orodruin.core.pathed_object import PathedObject


def test_implements_pathed_object() -> None:
    issubclass(Component, PathedObject)


def test_init_component(state: State) -> None:
    assert len(state.components()) == 0

    component = state.create_component("component")

    assert len(state.components()) == 1
    assert component.name() == "component"


def test_add_ports(state: State) -> None:

    component = state.create_component("component")

    assert len(component.ports()) == 0

    input1 = state.create_port("input1", PortDirection.input, int, component.uuid())
    input2 = state.create_port("input2", PortDirection.input, int, component.uuid())
    output = state.create_port("output", PortDirection.input, int, component.uuid())

    assert len(state.ports()) == 3

    component.register_port(input1)
    component.register_port(input2)
    component.register_port(output)

    assert len(component.ports()) == 3


def test_set_name(state: State) -> None:
    component = state.create_component("original_name")

    assert component.name() == "original_name"

    component.set_name("new_name")

    assert component.name() == "new_name"


def test_path_root_component(state: State) -> None:
    component = state.create_component("root")
    assert component.path() == PurePosixPath("/root")


def test_path_nested_component(state: State) -> None:
    root_component = state.create_component("root")
    child_a = state.create_component("child_a")
    child_b = state.create_component("child_b")

    child_a.set_parent_graph(root_component.graph().uuid())
    child_b.set_parent_graph(child_a.graph().uuid())

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative(state: State) -> None:
    root_component = state.create_component("root")
    child_a = state.create_component("child_a")
    child_b = state.create_component("child_b")

    child_a.set_parent_graph(root_component.graph().uuid())
    child_b.set_parent_graph(child_a.graph().uuid())

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port(state: State) -> None:
    component = state.create_component("component")
    port = state.create_port("input1", PortDirection.input, int, component.uuid())
    component.register_port(port)
    assert isinstance(component.port("input1"), Port)


def test_access_innexisting_port(state: State) -> None:
    component = state.create_component("component")
    with pytest.raises(NameError):
        component.port("this_is_not_a_port")
