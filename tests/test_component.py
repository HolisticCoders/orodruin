from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from orodruin.component import (
    Component,
    ComponentDoesNotExistError,
    ParentToSelfError,
)
from orodruin.port import Port


def test_init_component():
    component = Component("component")
    assert component.name() == "component"


def test_init_component_with_uuid():
    uuid = uuid4()
    component = Component("Component", uuid)
    assert component.uuid() == uuid


def test_get_component_from_uuid():
    component = Component("root")
    same_component = Component.from_uuid(component.uuid())

    assert component is same_component


def test_get_component_from_inexistant_uuid():
    with pytest.raises(ComponentDoesNotExistError):
        Component.from_uuid(uuid4())


def test_get_component_from_path():
    component = Component("root")
    same_component = Component.from_path("/root")

    assert component is same_component


def test_get_component_from_inexistant_path():
    with pytest.raises(ComponentDoesNotExistError):
        Component.from_path("/root")


def test_add_ports():
    component = Component("component")

    assert len(component.ports()) == 0

    component.add_port("input1")
    component.add_port("input2")
    component.add_port("output")

    assert len(component.ports()) == 3


def test_set_name():
    component = Component("original name")
    component.set_name("new name")

    assert component.name() == "new name"


def test_path_root_component():
    component = Component("root")
    assert component.path() == PurePosixPath("/root")


def test_path_nested_component():
    root = Component("root")
    child_a = Component("Child A")
    child_b = Component("Child B")

    child_a.set_parent(root)
    child_b.set_parent(child_a)

    assert child_b.path() == PurePosixPath("/root/Child A/Child B")


def test_access_port():
    component = Component("component")
    component.add_port("input1")
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
    parent = Component("parent")

    child_a = Component("child A")
    child_a.set_parent(parent)

    child_b = Component("child B")
    child_b.set_parent(parent)

    child_a.add_port("input1")
    child_a.add_port("input2")
    child_a.add_port("output")

    child_b.add_port("input1")
    child_b.add_port("input2")
    child_b.add_port("output")

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    expected_data = {
        "components": [
            {
                "components": [],
                "name": "child A",
                "ports": [
                    {"name": "input1", "source": None, "targets": []},
                    {"name": "input2", "source": None, "targets": []},
                    {
                        "name": "output",
                        "source": None,
                        "targets": [
                            PurePosixPath("child B.input1"),
                            PurePosixPath("child B.input2"),
                        ],
                    },
                ],
            },
            {
                "components": [],
                "name": "child B",
                "ports": [
                    {
                        "name": "input1",
                        "source": PurePosixPath("child A.output"),
                        "targets": [],
                    },
                    {
                        "name": "input2",
                        "source": PurePosixPath("child A.output"),
                        "targets": [],
                    },
                    {"name": "output", "source": None, "targets": []},
                ],
            },
        ],
        "name": "parent",
        "ports": [],
    }

    assert parent.as_dict() == expected_data


def test_as_json():
    parent = Component("parent")

    child_a = Component("child A")
    child_a.set_parent(parent)

    child_b = Component("child B")
    child_b.set_parent(parent)

    child_a.add_port("input1")
    child_a.add_port("input2")
    child_a.add_port("output")

    child_b.add_port("input1")
    child_b.add_port("input2")
    child_b.add_port("output")

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    parent.as_json()
