# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath
from typing import Generator

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.graph_manager import GraphManager
from orodruin.pathed_object import PathedObject
from orodruin.port import PortDirection, Port


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_implements_pathedobject() -> None:
    issubclass(Component, PathedObject)


def test_init_component() -> None:
    component = Component.new("component")
    assert component.name() == "component"


def test_add_ports() -> None:

    component = Component.new("component")

    assert len(component.ports()) == 0

    component.add_port("input1", PortDirection.input, int)
    component.add_port("input2", PortDirection.input, int)
    component.add_port("output", PortDirection.output, int)

    assert len(component.ports()) == 3


def test_set_name() -> None:
    component = Component.new("original_name")
    component.set_name("new_name")

    assert component.name() == "new_name"


def test_path_root_component() -> None:
    root_component = Component.new("root")
    assert root_component.path() == PurePosixPath("/root")


def test_path_nested_component() -> None:
    root_component = Component.new("root")
    child_a = Component.new("child_a")
    child_b = Component.new("child_b")

    child_a.set_parent(root_component)
    child_b.set_parent(child_a)

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative() -> None:
    root_component = Component.new("root")
    child_a = Component.new("child_a")
    child_b = Component.new("child_b")

    child_a.set_parent(root_component)
    child_b.set_parent(child_a)

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port() -> None:
    component = Component.new("component")
    component.add_port("input1", PortDirection.input, int)
    assert isinstance(component.input1, Port)


def test_access_innexisting_port() -> None:
    component = Component.new("component")
    with pytest.raises(NameError):
        component.this_is_not_a_port  # pylint: disable = pointless-statement


def test_parent_component() -> None:
    parent = Component.new("parent")
    child = Component.new("child")

    child.set_parent(parent)

    assert child.parent() is parent
    assert child in parent.components()


def test_parent_component_twice() -> None:
    parent = Component.new("parent")
    child = Component.new("child")

    child.set_parent(parent)
    child.set_parent(parent)

    assert parent.components().count(child) == 1


def test_parent_to_self() -> None:
    component = Component.new("component")

    with pytest.raises(ParentToSelfError):
        component.set_parent(component)
