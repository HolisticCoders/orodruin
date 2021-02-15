# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.graph_manager import GraphManager
from orodruin.port import Port, PortType


@pytest.fixture(autouse=True)
def clear_registered_components():

    yield
    GraphManager.clear_registered_components()


def test_init_component():
    component = Component("component")
    assert component.name() == "component"


def test_add_ports():

    component = Component("component")

    assert len(component.ports()) == 0

    component.add_port("input1", PortType.int)
    component.add_port("input2", PortType.int)
    component.add_port("output", PortType.int)

    assert len(component.ports()) == 3


def test_set_name():
    component = Component("original name")
    component.set_name("new name")

    assert component.name() == "new name"


def test_path_root_component():
    root_component = Component("root")
    assert root_component.path() == PurePosixPath("/root")


def test_path_nested_component():
    root_component = Component("root")
    child_a = Component("child_a")
    child_b = Component("child_b")

    child_a.set_parent(root_component)
    child_b.set_parent(child_a)

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_component_relative():
    root_component = Component("root")
    child_a = Component("child_a")
    child_b = Component("child_b")

    child_a.set_parent(root_component)
    child_b.set_parent(child_a)

    assert child_b.path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port():
    component = Component("component")
    component.add_port("input1", PortType.int)
    assert isinstance(component.input1, Port)


def test_access_innexisting_port():
    component = Component("component")
    assert component.this_is_not_a_port is None


def test_parent_component():
    parent = Component("parent")
    child = Component("child")

    child.set_parent(parent)

    assert child.parent() is parent
    assert child in parent.components()


def test_parent_component_twice():
    parent = Component("parent")
    child = Component("child")

    child.set_parent(parent)
    child.set_parent(parent)

    assert parent.components().count(child) == 1


def test_parent_to_self():
    component = Component("component")

    with pytest.raises(ParentToSelfError):
        component.set_parent(component)


def test_as_dict():
    root = Component("root")
    root.add_port("input1", PortType.int)
    root.add_port("input2", PortType.int)
    root.add_port("output", PortType.int)

    child_a = Component("child_a")
    child_a.set_parent(root)

    child_b = Component("child_b")
    child_b.set_parent(root)

    child_a.add_port("input1", PortType.int)
    child_a.add_port("input2", PortType.int)
    child_a.add_port("output", PortType.int)

    child_b.add_port("input1", PortType.int)
    child_b.add_port("input2", PortType.int)
    child_b.add_port("output", PortType.int)

    root.input1.connect(child_a.input1)
    root.input2.connect(child_a.input2)
    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)
    child_b.output.connect(root.output)

    expected_data = {
        "components": [
            {
                "components": [],
                "connections": [],
                "name": "child_a",
                "type": "Component",
                "ports": [
                    {
                        "name": "input1",
                        "type": "int",
                        "value": 0,
                    },
                    {
                        "name": "input2",
                        "type": "int",
                        "value": 0,
                    },
                    {
                        "name": "output",
                        "type": "int",
                        "value": 0,
                    },
                ],
            },
            {
                "components": [],
                "connections": [],
                "name": "child_b",
                "type": "Component",
                "ports": [
                    {
                        "name": "input1",
                        "type": "int",
                        "value": 0,
                    },
                    {
                        "name": "input2",
                        "type": "int",
                        "value": 0,
                    },
                    {
                        "name": "output",
                        "type": "int",
                        "value": 0,
                    },
                ],
            },
        ],
        "name": "root",
        "type": "Component",
        "ports": [
            {
                "name": "input1",
                "type": "int",
                "value": 0,
            },
            {
                "name": "input2",
                "type": "int",
                "value": 0,
            },
            {
                "name": "output",
                "type": "int",
                "value": 0,
            },
        ],
        "connections": [
            (PurePosixPath(".input1"), PurePosixPath("child_a.input1")),
            (PurePosixPath(".input2"), PurePosixPath("child_a.input2")),
            (PurePosixPath("child_a.output"), PurePosixPath("child_b.input1")),
            (PurePosixPath("child_a.output"), PurePosixPath("child_b.input2")),
            (PurePosixPath("child_b.output"), PurePosixPath(".output")),
        ],
    }

    assert root.as_dict() == expected_data
