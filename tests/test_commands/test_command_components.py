# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin import Component, Port, PortDirection
from orodruin.command.components import CreateComponent, DeleteComponent


def test_create_component_init(root: Component) -> None:
    CreateComponent(root.graph(), "my_component")


def test_create_port_do_undo_redo(root: Component) -> None:
    assert not root.graph().components()

    command = CreateComponent(root.graph(), "my_component")
    command.do()

    assert root.graph().components()

    command.undo()

    assert not root.graph().components()

    command.redo()

    assert root.graph().components()


def test_delete_component_init(root: Component) -> None:
    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    DeleteComponent(root.graph(), component.uuid())


def test_delete_component_do_undo_redo(root: Component) -> None:

    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    assert root.graph().components()

    command = DeleteComponent(root.graph(), component.uuid())
    command.do()

    assert not root.graph().components()

    command.undo()

    assert root.graph().components()

    command.redo()

    assert not root.graph().components()
