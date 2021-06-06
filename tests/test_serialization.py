# pylint: disable = missing-module-docstring, missing-function-docstring, cyclic-import
from pathlib import Path, PurePosixPath
from typing import Generator

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager
from orodruin.library import LibraryManager
from orodruin.port import PortDirection
from orodruin.port.types import Matrix
from orodruin.serialization import ComponentSerializer


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:
    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    yield

    GraphManager.clear_registered_components()

    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library.path)


def test_component_instance_data() -> None:
    root = Component.new("root")
    root.add_port("input1", PortDirection.input, int)
    root.add_port("input2", PortDirection.input, int)
    root.add_port("output", PortDirection.output, int)
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

    assert ComponentSerializer.component_instance_data(root) == expected_data


def test_component_definition_data() -> None:
    root = Component.new("root")
    root.add_port("input1", PortDirection.input, int)
    root.add_port("input2", PortDirection.input, int)
    root.add_port("output", PortDirection.output, int)

    child_a = Component.new("child_a")
    child_a.add_port("input1", PortDirection.input, int)
    child_a.add_port("input2", PortDirection.input, int)
    child_a.add_port("output", PortDirection.output, int)
    child_a.set_parent(root)

    child_b = Component.new("child_b")
    child_b.add_port("input1", PortDirection.input, int)
    child_b.add_port("input2", PortDirection.input, int)
    child_b.add_port("output", PortDirection.output, int)
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
                        "direction": "input",
                        "type": "int",
                    },
                    {
                        "name": "input2",
                        "direction": "input",
                        "type": "int",
                    },
                    {
                        "name": "output",
                        "direction": "output",
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
                        "direction": "input",
                        "type": "int",
                    },
                    {
                        "name": "input2",
                        "direction": "input",
                        "type": "int",
                    },
                    {
                        "name": "output",
                        "direction": "output",
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
                "direction": "input",
                "type": "int",
            },
            {
                "name": "input2",
                "direction": "input",
                "type": "int",
            },
            {
                "name": "output",
                "direction": "output",
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

    assert ComponentSerializer.component_definition_data(root) == expected_data


def test_component_as_json() -> None:
    root = Component.new("root")

    child_a = Component.new("child_a")
    child_a.add_port("input1", PortDirection.input, int)
    child_a.add_port("input2", PortDirection.input, int)
    child_a.add_port("output", PortDirection.output, int)
    child_a.set_parent(root)

    child_b = Component.new("child_b")
    child_b.add_port("input1", PortDirection.input, int)
    child_b.add_port("input2", PortDirection.input, int)
    child_b.add_port("output", PortDirection.output, int)
    child_b.set_parent(root)

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    ComponentSerializer.component_as_json(root)


def test_simple_component_from_json() -> None:
    component_name = "SimpleComponent"
    component = LibraryManager.get_component(component_name)
    component_file = (
        Path(__file__) / ".." / "TestLibrary" / "orodruin" / f"{component_name}.json"
    )
    with component_file.open("r") as handle:
        file_content = handle.read()

    assert ComponentSerializer.component_as_json(component) == file_content


def test_nested_component_from_json() -> None:
    component_name = "NestedComponent"
    component = LibraryManager.get_component(component_name)
    component_file = (
        Path(__file__) / ".." / "TestLibrary" / "orodruin" / f"{component_name}.json"
    )

    with component_file.open("r") as handle:
        file_content = handle.read()

    assert ComponentSerializer.component_as_json(component) == file_content


def test_referencing_component_from_json() -> None:
    component_name = "ReferencingSimpleComponent"
    component = LibraryManager.get_component(component_name)
    component_file = (
        Path(__file__) / ".." / "TestLibrary" / "orodruin" / f"{component_name}.json"
    )

    with component_file.open("r") as handle:
        file_content = handle.read()

    assert ComponentSerializer.component_as_json(component) == file_content


def test_referencing_nested_component_from_json() -> None:
    component_name = "ReferencingNestedComponent"
    component = LibraryManager.get_component(component_name)
    component_file = (
        Path(__file__) / ".." / "TestLibrary" / "orodruin" / f"{component_name}.json"
    )

    with component_file.open("r") as handle:
        file_content = handle.read()

    assert ComponentSerializer.component_as_json(component) == file_content


def test_serialize_custom_port_type() -> None:
    root = Component.new("root")

    sub_component = Component.new("sub_component")
    sub_component.set_parent(root)

    sub_component.add_port("matrix", PortDirection.input, Matrix)
    ComponentSerializer.component_as_json(root)
