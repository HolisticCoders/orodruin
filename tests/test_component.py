from uuid import uuid4

import pytest

from orodruin.component import Component, ParentToSelfError
from orodruin.port import Port, PortSide


def test_init_component():
    component = Component("component")
    assert component.name() == "component"


def test_init_component_with_uuid():
    uuid = uuid4()
    component = Component("Component", uuid)
    assert component.uuid() == uuid


def test_add_ports():
    component = Component("component")

    assert len(component.inputs()) == 0
    assert len(component.outputs()) == 0

    component.add_port("input1", PortSide.input)
    component.add_port("input2", PortSide.input)
    component.add_port("output", PortSide.output)

    assert len(component.inputs()) == 2
    assert len(component.outputs()) == 1


def test_set_name():
    component = Component("original name")
    component.set_name("new name")

    assert component.name() == "new name"


def test_access_port():
    component = Component("component")
    component.add_port("input1", PortSide.input)
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

    child_a.add_port("input1", PortSide.input)
    child_a.add_port("input2", PortSide.input)
    child_a.add_port("output", PortSide.output)

    child_b.add_port("input1", PortSide.input)
    child_b.add_port("input2", PortSide.input)
    child_b.add_port("output", PortSide.output)

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    expected_data = {
        "name": "parent",
        "uuid": parent.uuid(),
        "components": [
            {
                "name": "child A",
                "uuid": child_a.uuid(),
                "components": [],
                "inputs": [
                    {
                        "name": "input1",
                        "uuid": child_a.input1.uuid(),
                        "connections": [],
                    },
                    {
                        "name": "input2",
                        "uuid": child_a.input2.uuid(),
                        "connections": [],
                    },
                ],
                "outputs": [
                    {
                        "name": "output",
                        "uuid": child_a.output.uuid(),
                        "connections": [
                            child_b.input1.uuid(),
                            child_b.input2.uuid(),
                        ],
                    },
                ],
            },
            {
                "name": "child B",
                "uuid": child_b.uuid(),
                "components": [],
                "inputs": [
                    {
                        "name": "input1",
                        "uuid": child_b.input1.uuid(),
                        "connections": [child_a.output.uuid()],
                    },
                    {
                        "name": "input2",
                        "uuid": child_b.input2.uuid(),
                        "connections": [child_a.output.uuid()],
                    },
                ],
                "outputs": [
                    {
                        "name": "output",
                        "uuid": child_b.output.uuid(),
                        "connections": [],
                    },
                ],
            },
        ],
        "inputs": [],
        "outputs": [],
    }

    assert parent.as_dict() == expected_data


def test_as_json():
    parent = Component("parent")

    child_a = Component("child A")
    child_a.set_parent(parent)

    child_b = Component("child B")
    child_b.set_parent(parent)

    child_a.add_port("input1", PortSide.input)
    child_a.add_port("input2", PortSide.input)
    child_a.add_port("output", PortSide.output)

    child_b.add_port("input1", PortSide.input)
    child_b.add_port("input2", PortSide.input)
    child_b.add_port("output", PortSide.output)

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    parent.as_json()
