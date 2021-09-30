# pylint: disable = missing-module-docstring, missing-function-docstring, cyclic-import
from pathlib import Path
from typing import Generator

import pytest

from orodruin.commands import (
    ConnectPorts,
    CreateNode,
    CreatePort,
    ExportNode,
    ImportNode,
)
from orodruin.core import LibraryManager, PortDirection, State


@pytest.fixture(autouse=True)
def clear_registered_nodes() -> Generator:
    library_path = Path(__file__).parent.parent / "TestLibrary"
    LibraryManager.register_library(library_path)

    yield

    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library.path())


def test_node_instance_data(state: State) -> None:
    node = CreateNode(state, "multiply").do()
    CreatePort(state, node, "input1", PortDirection.input, int).do()
    CreatePort(state, node, "input2", PortDirection.input, int).do()
    CreatePort(state, node, "output", PortDirection.output, int).do()

    node.port("input1").set(2)
    node.port("input2").set(2)
    node.port("output").set(4)

    command = ExportNode(node, "DummyName")

    expected_data = {
        "type": f"Internal::{node.type()}",
        "name": "multiply",
        "ports": {
            "input1": 2,
            "input2": 2,
            "output": 4,
        },
    }

    assert command._node_instance_data(node) == expected_data


def test_node_definition_data(state: State) -> None:
    parent = CreateNode(state, "parent").do()
    CreatePort(state, parent, "input1", PortDirection.input, int).do()
    CreatePort(state, parent, "input2", PortDirection.input, int).do()
    CreatePort(state, parent, "output", PortDirection.output, int).do()

    child_a = CreateNode(state, "child_a", graph=parent.graph()).do()
    CreatePort(state, child_a, "input1", PortDirection.input, int).do()
    CreatePort(state, child_a, "input2", PortDirection.input, int).do()
    CreatePort(state, child_a, "output", PortDirection.output, int).do()

    child_b = CreateNode(state, "child_b", graph=parent.graph()).do()
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

    command = ExportNode(parent, "DummyName")

    expected_data = {
        "definitions": {
            str(child_a.type()): {
                "definitions": {},
                "nodes": [],
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
                "nodes": [],
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
        "nodes": [
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

    assert command._node_definition_data(parent) == expected_data


def test_node_as_json(state: State) -> None:
    parent = CreateNode(state, "parent").do()
    CreatePort(state, parent, "input1", PortDirection.input, int).do()
    CreatePort(state, parent, "input2", PortDirection.input, int).do()
    CreatePort(state, parent, "output", PortDirection.output, int).do()

    child_a = CreateNode(state, "child_a", graph=parent.graph()).do()
    CreatePort(state, child_a, "input1", PortDirection.input, int).do()
    CreatePort(state, child_a, "input2", PortDirection.input, int).do()
    CreatePort(state, child_a, "output", PortDirection.output, int).do()

    child_b = CreateNode(state, "child_b", graph=parent.graph()).do()
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

    ExportNode._node_as_json(parent)  # pylint: disable = protected-access


def test_export_node(state: State) -> None:
    node = CreateNode(state, "multiply").do()
    CreatePort(state, node, "input1", PortDirection.input, int).do()
    CreatePort(state, node, "input2", PortDirection.input, int).do()
    CreatePort(state, node, "output", PortDirection.output, int).do()

    node.port("input1").set(2)
    node.port("input2").set(2)
    node.port("output").set(4)

    command = ExportNode(node, "TestLibrary")
    file_path = command.do()

    assert file_path.exists()
    file_path.unlink()


def test_import_simple_node(state: State) -> None:
    node_name = "SimpleNode"
    node = ImportNode(
        state,
        state.root_graph(),
        node_name,
        "TestLibrary",
    ).do()

    file_path = (
        Path(__file__).parent.parent / "TestLibrary" / "orodruin" / f"{node_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportNode(
    #     node,
    #     "TestLibrary",
    #     node_name=f"{node_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportNode._node_as_json(node) == file_content


def test_import_nested_node(state: State) -> None:
    node_name = "NestedNode"
    node = ImportNode(state, state.root_graph(), node_name, "TestLibrary").do()

    file_path = (
        Path(__file__).parent.parent / "TestLibrary" / "orodruin" / f"{node_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportNode(
    #     node,
    #     "TestLibrary",
    #     node_name=f"{node_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportNode._node_as_json(node) == file_content


def test_import_referencing_node(state: State) -> None:
    node_name = "ReferencingSimpleNode"
    node = ImportNode(state, state.root_graph(), node_name, "TestLibrary").do()

    file_path = (
        Path(__file__).parent.parent / "TestLibrary" / "orodruin" / f"{node_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportNode(
    #     node,
    #     "TestLibrary",
    #     node_name=f"{node_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportNode._node_as_json(node) == file_content


def test_import_referencing_nested_node(state: State) -> None:
    node_name = "ReferencingNestedNode"
    node = ImportNode(state, state.root_graph(), node_name, "TestLibrary").do()

    file_path = (
        Path(__file__).parent.parent / "TestLibrary" / "orodruin" / f"{node_name}.json"
    )
    with file_path.open("r") as f:
        file_content = f.read()

    # ExportNode(
    #     node,
    #     "TestLibrary",
    #     node_name=f"{node_name}_test",
    # ).do()

    # pylint: disable = protected-access
    assert ExportNode._node_as_json(node) == file_content
