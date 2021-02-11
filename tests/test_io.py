# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import Path

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager
from orodruin.io import component_as_json, component_from_json
from orodruin.library import (
    get_component,
    list_libraries,
    register_library,
    unregister_library,
)
from orodruin.port import PortType


@pytest.fixture(autouse=True)
def clear_registered_components():
    library_path = (Path(__file__) / ".." / "library").resolve()
    register_library(library_path)

    yield

    GraphManager.clear_registered_components()

    for library in list_libraries():
        unregister_library(library)


def test_component_as_json():
    parent = Component("parent")

    child_a = Component("child A")
    child_a.set_parent(parent)

    child_b = Component("child B")
    child_b.set_parent(parent)

    child_a.add_port("input1", PortType.int)
    child_a.add_port("input2", PortType.int)
    child_a.add_port("output", PortType.int)

    child_b.add_port("input1", PortType.int)
    child_b.add_port("input2", PortType.int)
    child_b.add_port("output", PortType.int)

    child_a.output.connect(child_b.input1)
    child_a.output.connect(child_b.input2)

    component_as_json(parent)


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
