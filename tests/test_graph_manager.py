# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Generator

import pytest

from orodruin.component import Component
from orodruin.graph_manager import ComponentDoesNotExistError, GraphManager


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_register_component() -> None:
    assert len(GraphManager.components()) == 0

    Component.new("component")

    assert len(GraphManager.components()) == 1


def test_get_component_from_path() -> None:
    root_component = Component.new("root")
    same_component = GraphManager.component_from_path("/root")

    assert root_component is same_component


def test_get_component_from_inexistant_path() -> None:
    with pytest.raises(ComponentDoesNotExistError):
        GraphManager.component_from_path("/root")
