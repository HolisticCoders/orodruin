# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath
from typing import Generator

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.graph_manager import GraphManager
from orodruin.pathed_object import PathedObject
from orodruin.port import Port, PortDirection


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_implements_pathedobject() -> None:
    issubclass(Component, PathedObject)


def test_init_component() -> None:
    component = Component("component")
    assert component.name() == "component"


def test_add_ports() -> None:

    component = Component("component")

    assert len(component.ports()) == 0

    component.register_port("input1", PortDirection.input, int)
    component.register_port("input2", PortDirection.input, int)
    component.register_port("output", PortDirection.output, int)

    assert len(component.ports()) == 3


def test_set_name() -> None:
    component = Component("original_name")
    component.set_name("new_name")

    assert component.name() == "new_name"


def test_path_root_component() -> None:
    root_component = Component("root")
    assert root_component.path() == PurePosixPath("/root")


def test_path_nested_component() -> None:
    root_component = Component("root")
    child_a = Component("child_a")
    child_b = Component("child_b")

    child_a.set_parent_graph(root_component)
    child_b.set_parent_graph(child_a)

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative() -> None:
    root_component = Component("root")
    child_a = Component("child_a")
    child_b = Component("child_b")

    child_a.set_parent_graph(root_component)
    child_b.set_parent_graph(child_a)

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port() -> None:
    component = Component("component")
    component.register_port("input1", PortDirection.input, int)
    assert isinstance(component.input1, Port)


def test_access_innexisting_port() -> None:
    component = Component("component")
    with pytest.raises(NameError):
        component.this_is_not_a_port  # pylint: disable = pointless-statement


def test_parent_component() -> None:
    parent = Component("parent")
    child = Component("child")

    child.set_parent_graph(parent)

    assert child.parent_graph() is parent
    assert child in parent.components()


def test_parent_component_twice() -> None:
    parent = Component("parent")
    child = Component("child")

    child.set_parent_graph(parent)
    child.set_parent_graph(parent)

    assert parent.components().count(child) == 1


def test_parent_to_self() -> None:
    component = Component("component")

    with pytest.raises(ParentToSelfError):
        component.set_parent_graph(component)
