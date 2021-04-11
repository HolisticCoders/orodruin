# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.graph_manager import GraphManager
from orodruin.port import Port, SinglePort


@pytest.fixture(autouse=True)
def clear_registered_components():

    yield
    GraphManager.clear_registered_components()


def test_init_component():
    component = Component.new("component")
    assert component.name == "component"


def test_add_ports():

    component = Component.new("component")

    assert len(component.ports) == 0

    component.add_port("input1", Port.Direction.input, int)
    component.add_port("input2", Port.Direction.input, int)
    component.add_port("output", Port.Direction.output, int)

    assert len(component.ports) == 3


def test_set_name():
    component = Component.new("original_name")
    component.name = "new_name"

    assert component.name == "new_name"


def test_path_root_component():
    root_component = Component.new("root")
    assert root_component.path == PurePosixPath("/root")


def test_path_nested_component():
    root_component = Component.new("root")
    child_a = Component.new("child_a")
    child_b = Component.new("child_b")

    child_a.parent = root_component
    child_b.parent = child_a

    assert child_b.path == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative():
    root_component = Component.new("root")
    child_a = Component.new("child_a")
    child_b = Component.new("child_b")

    child_a.parent = root_component
    child_b.parent = child_a

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port():
    component = Component.new("component")
    component.add_port("input1", Port.Direction.input, int)
    assert isinstance(component.input1, SinglePort)


def test_access_innexisting_port():
    component = Component.new("component")
    with pytest.raises(NameError):
        component.this_is_not_a_port  # pylint: disable = pointless-statement


def test_parent_component():
    parent = Component.new("parent")
    child = Component.new("child")

    child.parent = parent

    assert child.parent is parent
    assert child in parent.components


def test_parent_component_twice():
    parent = Component.new("parent")
    child = Component.new("child")

    child.parent = parent
    child.parent = parent

    assert parent.components.count(child) == 1


def test_parent_to_self():
    component = Component.new("component")

    with pytest.raises(ParentToSelfError):
        component.parent = component
