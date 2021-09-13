# pylint: disable = missing-module-docstring, missing-function-docstring, cyclic-import
from pathlib import Path, PurePosixPath
from typing import Generator

import pytest

from orodruin.commands import ConnectPorts, CreateComponent, CreatePort, ExportComponent
from orodruin.component import Component
from orodruin.library import LibraryManager
from orodruin.port import PortDirection
from orodruin.port.types import Matrix


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:
    library_path = Path(__file__).parent.parent / "TestLibrary"
    LibraryManager.register_library(library_path)

    yield

    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library._path)


def test_component_instance_data(root: Component) -> None:
    component = CreateComponent(root.graph(), "multiply").do()
    CreatePort(root.graph(), component, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), component, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), component, "output", PortDirection.output, int).do()

    component.input1.set(2)
    component.input2.set(2)
    component.output.set(4)

    command = ExportComponent(component, "DummyName")

    expected_data = {
        "type": f"Internal::{component.type()}",
        "name": "multiply",
        "ports": {
            "input1": 2,
            "input2": 2,
            "output": 4,
        },
    }

    assert command._component_instance_data(component) == expected_data


def test_component_definition_data(root: Component) -> None:
    parent = CreateComponent(root.graph(), "parent").do()
    CreatePort(root.graph(), parent, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), parent, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), parent, "output", PortDirection.output, int).do()

    child_a = CreateComponent(parent.graph(), "child_a").do()
    CreatePort(root.graph(), child_a, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), child_a, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), child_a, "output", PortDirection.output, int).do()

    child_b = CreateComponent(parent.graph(), "child_b").do()
    CreatePort(root.graph(), child_b, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), child_b, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), child_b, "output", PortDirection.output, int).do()

    ConnectPorts(parent.graph(), parent.input1, child_a.input1).do()
    ConnectPorts(parent.graph(), parent.input2, child_a.input2).do()
    ConnectPorts(parent.graph(), child_a.output, child_b.input1).do()
    ConnectPorts(parent.graph(), child_a.output, child_b.input2).do()
    ConnectPorts(parent.graph(), child_b.output, parent.output).do()

    command = ExportComponent(parent, "DummyName")

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
            (".input1", "child_a.input1"),
            (".input2", "child_a.input2"),
            ("child_a.output", "child_b.input1"),
            ("child_a.output", "child_b.input2"),
            ("child_b.output", ".output"),
        ],
    }

    assert command._component_definition_data(parent) == expected_data


def test_component_as_json(root: Component) -> None:
    parent = CreateComponent(root.graph(), "parent").do()
    CreatePort(root.graph(), parent, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), parent, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), parent, "output", PortDirection.output, int).do()

    child_a = CreateComponent(parent.graph(), "child_a").do()
    CreatePort(root.graph(), child_a, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), child_a, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), child_a, "output", PortDirection.output, int).do()

    child_b = CreateComponent(parent.graph(), "child_b").do()
    CreatePort(root.graph(), child_b, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), child_b, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), child_b, "output", PortDirection.output, int).do()

    ConnectPorts(parent.graph(), parent.input1, child_a.input1).do()
    ConnectPorts(parent.graph(), parent.input2, child_a.input2).do()
    ConnectPorts(parent.graph(), child_a.output, child_b.input1).do()
    ConnectPorts(parent.graph(), child_a.output, child_b.input2).do()
    ConnectPorts(parent.graph(), child_b.output, parent.output).do()

    command = ExportComponent(parent, "DummyName")
    command._component_as_json()


def test_export_component(root: Component) -> None:
    component = CreateComponent(root.graph(), "multiply").do()
    CreatePort(root.graph(), component, "input1", PortDirection.input, int).do()
    CreatePort(root.graph(), component, "input2", PortDirection.input, int).do()
    CreatePort(root.graph(), component, "output", PortDirection.output, int).do()

    component.input1.set(2)
    component.input2.set(2)
    component.output.set(4)

    command = ExportComponent(component, "DummyName")

    expected_data = {
        "type": f"Internal::{component.type()}",
        "name": "multiply",
        "ports": {
            "input1": 2,
            "input2": 2,
            "output": 4,
        },
    }

    assert command._component_instance_data(component) == expected_data


# def test_simple_component_from_json() -> None:
#     component_name = "SimpleComponent"
#     component = LibraryManager.get_component(component_name)
#     component_file = (
#         Path(__file__).parent / "TestLibrary" / "orodruin" / f"{component_name}.json"
#     )
#     with component_file.open("r") as handle:
#         file_content = handle.read()

#     assert ComponentSerializer.component_as_json(component) == file_content


# def test_nested_component_from_json() -> None:
#     component_name = "NestedComponent"
#     component = LibraryManager.get_component(component_name)
#     component_file = (
#         Path(__file__).parent / "TestLibrary" / "orodruin" / f"{component_name}.json"
#     )

#     with component_file.open("r") as handle:
#         file_content = handle.read()

#     assert ComponentSerializer.component_as_json(component) == file_content


# def test_referencing_component_from_json() -> None:
#     component_name = "ReferencingSimpleComponent"
#     component = LibraryManager.get_component(component_name)
#     component_file = (
#         Path(__file__).parent / "TestLibrary" / "orodruin" / f"{component_name}.json"
#     )

#     with component_file.open("r") as handle:
#         file_content = handle.read()

#     assert ComponentSerializer.component_as_json(component) == file_content


# def test_referencing_nested_component_from_json() -> None:
#     component_name = "ReferencingNestedComponent"
#     component = LibraryManager.get_component(component_name)
#     component_file = (
#         Path(__file__).parent / "TestLibrary" / "orodruin" / f"{component_name}.json"
#     )

#     with component_file.open("r") as handle:
#         file_content = handle.read()

#     assert ComponentSerializer.component_as_json(component) == file_content


# def test_serialize_custom_port_type() -> None:
#     root = Component("root")

#     sub_component = Component("sub_component")
#     sub_component.set_parent_graph(root)

#     sub_component.register_port("matrix", PortDirection.input, Matrix)
#     ComponentSerializer.component_as_json(root)
