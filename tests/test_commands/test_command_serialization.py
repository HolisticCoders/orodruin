# pylint: disable = missing-module-docstring, missing-function-docstring, cyclic-import
from pathlib import Path
from typing import Generator

import pytest

from orodruin.commands import (
    ConnectPorts,
    CreateComponent,
    CreatePort,
    ExportComponent,
    ImportComponent,
)
from orodruin.core import LibraryManager, PortDirection, State


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:
    library_path = Path(__file__).parent.parent / "TestLibrary"
    LibraryManager.register_library(library_path)

    yield

    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library.path())


def test_component_instance_data(state: State) -> None:
    component = CreateComponent(state, "multiply").do()
    CreatePort(state, component, "input1", PortDirection.input, int).do()
    CreatePort(state, component, "input2", PortDirection.input, int).do()
    CreatePort(state, component, "output", PortDirection.output, int).do()

    component.port("input1").set(2)
    component.port("input2").set(2)
    component.port("output").set(4)

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


def test_component_definition_data(state: State) -> None:
    parent = CreateComponent(state, "parent").do()
    CreatePort(state, parent, "input1", PortDirection.input, int).do()
    CreatePort(state, parent, "input2", PortDirection.input, int).do()
    CreatePort(state, parent, "output", PortDirection.output, int).do()

    child_a = CreateComponent(state, "child_a", graph=parent.graph()).do()
    CreatePort(state, child_a, "input1", PortDirection.input, int).do()
    CreatePort(state, child_a, "input2", PortDirection.input, int).do()
    CreatePort(state, child_a, "output", PortDirection.output, int).do()

    child_b = CreateComponent(state, "child_b", graph=parent.graph()).do()
    CreatePort(state, child_b, "input1", PortDirection.input, int).do()
    CreatePort(state, child_b, "input2", PortDirection.input, int).do()
    CreatePort(state, child_b, "output", PortDirection.output, int).do()

    ConnectPorts(
        state, parent.graph(), parent.port("input1"), child_a.port("input1")
    ).do()
    ConnectPorts(
        state, parent.graph(), parent.port("input2"), child_a.port("input2")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_a.port("output"), child_b.port("input1")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_a.port("output"), child_b.port("input2")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_b.port("output"), parent.port("output")
    ).do()

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


def test_component_as_json(state: State) -> None:
    parent = CreateComponent(state, "parent").do()
    CreatePort(state, parent, "input1", PortDirection.input, int).do()
    CreatePort(state, parent, "input2", PortDirection.input, int).do()
    CreatePort(state, parent, "output", PortDirection.output, int).do()

    child_a = CreateComponent(state, "child_a", graph=parent.graph()).do()
    CreatePort(state, child_a, "input1", PortDirection.input, int).do()
    CreatePort(state, child_a, "input2", PortDirection.input, int).do()
    CreatePort(state, child_a, "output", PortDirection.output, int).do()

    child_b = CreateComponent(state, "child_b", graph=parent.graph()).do()
    CreatePort(state, child_b, "input1", PortDirection.input, int).do()
    CreatePort(state, child_b, "input2", PortDirection.input, int).do()
    CreatePort(state, child_b, "output", PortDirection.output, int).do()

    ConnectPorts(
        state, parent.graph(), parent.port("input1"), child_a.port("input1")
    ).do()
    ConnectPorts(
        state, parent.graph(), parent.port("input2"), child_a.port("input2")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_a.port("output"), child_b.port("input1")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_a.port("output"), child_b.port("input2")
    ).do()
    ConnectPorts(
        state, parent.graph(), child_b.port("output"), parent.port("output")
    ).do()

    ExportComponent._component_as_json(parent)  # pylint: disable = protected-access


def test_export_component(state: State) -> None:
    component = CreateComponent(state, "multiply").do()
    CreatePort(state, component, "input1", PortDirection.input, int).do()
    CreatePort(state, component, "input2", PortDirection.input, int).do()
    CreatePort(state, component, "output", PortDirection.output, int).do()

    component.port("input1").set(2)
    component.port("input2").set(2)
    component.port("output").set(4)

    command = ExportComponent(component, "TestLibrary")
    file_path = command.do()

    assert file_path.exists()
    file_path.unlink()


def test_import_simple_component(state: State) -> None:
    component_name = "SimpleComponent"
    component = ImportComponent(
        state,
        state.root_graph(),
        component_name,
        "TestLibrary",
    ).do()

    file_path = (
        Path(__file__).parent.parent
        / "TestLibrary"
        / "orodruin"
        / f"{component_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportComponent(
    #     component,
    #     "TestLibrary",
    #     component_name=f"{component_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportComponent._component_as_json(component) == file_content


def test_import_nested_component(state: State) -> None:
    component_name = "NestedComponent"
    component = ImportComponent(
        state, state.root_graph(), component_name, "TestLibrary"
    ).do()

    file_path = (
        Path(__file__).parent.parent
        / "TestLibrary"
        / "orodruin"
        / f"{component_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportComponent(
    #     component,
    #     "TestLibrary",
    #     component_name=f"{component_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportComponent._component_as_json(component) == file_content


def test_import_referencing_component(state: State) -> None:
    component_name = "ReferencingSimpleComponent"
    component = ImportComponent(
        state, state.root_graph(), component_name, "TestLibrary"
    ).do()

    file_path = (
        Path(__file__).parent.parent
        / "TestLibrary"
        / "orodruin"
        / f"{component_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportComponent(
    #     component,
    #     "TestLibrary",
    #     component_name=f"{component_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportComponent._component_as_json(component) == file_content


def test_import_referencing_nested_component(state: State) -> None:
    component_name = "ReferencingNestedComponent"
    component = ImportComponent(
        state, state.root_graph(), component_name, "TestLibrary"
    ).do()

    file_path = (
        Path(__file__).parent.parent
        / "TestLibrary"
        / "orodruin"
        / f"{component_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportComponent(
    #     component,
    #     "TestLibrary",
    #     component_name=f"{component_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportComponent._component_as_json(component) == file_content
