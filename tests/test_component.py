# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath
from typing import Callable
from uuid import uuid4

import pytest

from orodruin.component import (
    Component,
    ComponentDoesNotExistError,
    ParentToSelfError,
)
from orodruin.port import Port


def test_init_component(create_component: Callable[..., Component]):
    component = create_component("component")
    assert component.name() == "component"


def test_init_component_with_uuid(create_component: Callable[..., Component]):
    uuid = uuid4()
    component = create_component("Component", uuid)
    assert component.uuid() == uuid


def test_get_component_from_uuid(root_component: Component):
    same_component = Component.from_uuid(root_component.uuid())

    assert root_component is same_component


def test_get_component_from_inexistant_uuid():
    with pytest.raises(ComponentDoesNotExistError):
        Component.from_uuid(uuid4())


def test_get_component_from_path(root_component: Component):
    same_component = Component.from_path("/root")

    assert root_component is same_component


def test_get_component_from_inexistant_path():
    with pytest.raises(ComponentDoesNotExistError):
        Component.from_path("/root")


def test_add_ports(create_component: Callable[..., Component]):

    component = create_component("component")

    assert len(component.ports()) == 0

    component.add_port("input1")
    component.add_port("input2")
    component.add_port("output")

    assert len(component.ports()) == 3


def test_set_name(create_component: Callable[..., Component]):
    component = create_component("original name")
    component.set_name("new name")

    assert component.name() == "new name"


def test_path_root_component(root_component: Component):
    assert root_component.path() == PurePosixPath("/root")


def test_path_nested_component(
    root_component: Component,
    create_component: Callable[..., Component],
):
    child_a = create_component("Child A")
    child_b = create_component("Child B")

    child_a.set_parent(root_component)
    child_b.set_parent(child_a)

    assert child_b.path() == PurePosixPath("/root/Child A/Child B")


def test_access_port(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port("input1")
    assert isinstance(component.input1, Port)


def test_access_innexisting_port(create_component: Callable[..., Component]):
    component = create_component("component")
    assert component.this_is_not_a_port is None


def test_parent_component(create_component: Callable[..., Component]):
    parent = create_component("parent")
    child = create_component("child")

    child.set_parent(parent)

    assert child.parent() is parent
    assert child in parent.components()


def test_parent_component_twice(create_component: Callable[..., Component]):
    parent = create_component("parent")
    child = create_component("child")

    child.set_parent(parent)
    child.set_parent(parent)

    assert parent.components().count(child) == 1


def test_parent_to_self(create_component: Callable[..., Component]):
    component = create_component("component")

    with pytest.raises(ParentToSelfError):
        component.set_parent(component)


def test_as_dict(create_component: Callable[..., Component]):
    parent = create_component("parent")

    child_a = create_component("child A")
    child_a.set_parent(parent)

    child_b = create_component("child B")
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


def test_as_json(create_component: Callable[..., Component]):
    parent = create_component("parent")

    child_a = create_component("child A")
    child_a.set_parent(parent)

    child_b = create_component("child B")
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
