# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath
from typing import Callable

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.pathed_object import PathedObject
from orodruin.port import Port, PortDirection


def test_implements_pathedobject() -> None:
    issubclass(Component, PathedObject)


def test_init_component() -> None:
    component = Component("component")
    assert component.name() == "component"


def test_add_ports() -> None:

    component = Component("component")

    assert len(component.ports()) == 0

    input1 = Port("input1", PortDirection.input, int, component)
    input2 = Port("input2", PortDirection.input, int, component)
    output = Port("output", PortDirection.input, int, component)

    component.register_port(input1)
    component.register_port(input2)
    component.register_port(output)

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

    child_a.set_parent_graph(root_component.graph())
    child_b.set_parent_graph(child_a.graph())

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative() -> None:
    root_component = Component("root")
    child_a = Component("child_a")
    child_b = Component("child_b")

    child_a.set_parent_graph(root_component.graph())
    child_b.set_parent_graph(child_a.graph())

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port(create_port: Callable[..., Port]) -> None:
    component = Component("component")
    create_port(component, "input1")
    assert isinstance(component.input1, Port)


def test_access_innexisting_port() -> None:
    component = Component("component")
    with pytest.raises(NameError):
        component.this_is_not_a_port  # pylint: disable = pointless-statement
