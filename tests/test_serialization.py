# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import Path, PurePosixPath

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager
from orodruin.library import (
    get_component,
    list_libraries,
    register_library,
    unregister_library,
)
from orodruin.port import PortType
from orodruin.serialization import (
    component_as_json,
    component_definition_data,
    component_from_json,
    component_instance_data,
)


@pytest.fixture(autouse=True)
def clear_registered_components():
    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    register_library(library_path)

    yield

    GraphManager.clear_registered_components()

    for library in list_libraries():
        unregister_library(library)


def test_component_instance_data():
    root = Component("root")
    root.add_port("input1", PortType.int)
    root.add_port("input2", PortType.int)
    root.add_port("output", PortType.int)
    root.input1.set(1)
    root.input2.set(2)
    root.output.set(3)

    expected_data = {
        "type": f"Internal::{root.type()}",
        "name": "root",
        "ports": {
            "input1": 1,
            "input2": 2,
            "output": 3,
        },
    }

    assert component_instance_data(root) == expected_data


def test_component_definition_data():
    root = Component("root")
    root.add_port("input1", PortType.int)
    root.add_port("input2", PortType.int)
    root.add_port("output", PortType.int)

    child_a = Component("child_a")
    child_a.add_port("input1", PortType.int)
    child_a.add_port("input2", PortType.int)
    child_a.add_port("output", PortType.int)
    child_a.set_parent(root)

    child_b = Component("child_b")
    child_b.add_port("input1", PortType.int)
    child_b.add_port("input2", PortType.int)
    child_b.add_port("output", PortType.int)
    child_b.set_parent(root)

    root.input1.connect(child_a.input1)
    root.input2.connect(child_a.input2)
    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)
    child_b.output.connect(root.output)

    expected_data = {
        "definitions": {
            str(child_a.type()): {
                "definitions": {},
                "components": [],
                "connections": [],
                "ports": [
                    {
                        "name": "input1",
                        "type": "int",
                    },
                    {
                        "name": "input2",
                        "type": "int",
                    },
                    {
                        "name": "output",
                        "type": "int",
                    },
                ],
            },
            str(child_b.type()): {
                "definitions": {},
                "components": [],
                "connections": [],
                "ports": [
                    {
                        "name": "input1",
                        "type": "int",
                    },
                    {
                        "name": "input2",
                        "type": "int",
                    },
                    {
                        "name": "output",
                        "type": "int",
                    },
                ],
            },
        },
        "components": [
            {
                "name": "child_a",
                "type": f"Internal::{child_a.type()}",
                "ports": {
                    "input1": 0,
                    "input2": 0,
                    "output": 0,
                },
            },
            {
                "name": "child_b",
                "type": f"Internal::{child_b.type()}",
                "ports": {
                    "input1": 0,
                    "input2": 0,
                    "output": 0,
                },
            },
        ],
        "ports": [
            {
                "name": "input1",
                "type": "int",
            },
            {
                "name": "input2",
                "type": "int",
            },
            {
                "name": "output",
                "type": "int",
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

    assert component_definition_data(root) == expected_data


def test_component_as_json():
    root = Component("root")

    child_a = Component("child_a")
    child_a.add_port("input1", PortType.int)
    child_a.add_port("input2", PortType.int)
    child_a.add_port("output", PortType.int)
    child_a.set_parent(root)

    child_b = Component("child_b")
    child_b.add_port("input1", PortType.int)
    child_b.add_port("input2", PortType.int)
    child_b.add_port("output", PortType.int)
    child_b.set_parent(root)

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    component_as_json(root)


def test_simple_component_from_json():
    component_file = get_component("SimpleComponent")

    component = component_from_json(component_file)

    with open(component_file, "r") as handle:
        file_content = handle.read()

    assert component_as_json(component) == file_content


def test_nested_component_from_json():
    component_file = get_component("NestedComponent")
    component = component_from_json(component_file)

    with open(component_file, "r") as handle:
        file_content = handle.read()

    assert component_as_json(component) == file_content


def test_referencing_component_from_json():
    component_file = get_component("ReferencingSimpleComponent")
    component = component_from_json(component_file)

    with open(component_file, "r") as handle:
        file_content = handle.read()

    assert component_as_json(component) == file_content


def test_referencing_nested_component_from_json():
    component_file = get_component("ReferencingNestedComponent")
    component = component_from_json(component_file)

    with open(component_file, "r") as handle:
        file_content = handle.read()

    # FIXME: Fails because there is no difference between an internal and
    # external connection.
    # The `component_as_json` thinks that the new component is connected to its inner
    # component but the ReferencingNestedComponent doesn't define that.
    assert component_as_json(component) == file_content
