# pylint: disable = missing-module-docstring, missing-function-docstring
import pytest

from orodruin.component import Component
from orodruin.io import component_as_json
from orodruin.port import PortType


@pytest.fixture(autouse=True)
def delete_components():
    yield
    Component._instances = {}  # pylint: disable = protected-access


def test_as_json():
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
