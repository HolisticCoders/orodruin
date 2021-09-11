# pylint: disable = missing-module-docstring, missing-function-docstring
from typing import Callable

import pytest

from orodruin import Component, Port, PortDirection
from orodruin.command.components import CreateComponent


def test_create_component_init(root: Component) -> None:
    CreateComponent(root.graph(), "my_component")


def test_connect_port_do_undo_redo(root: Component) -> None:
    assert not root.graph().components()

    command = CreateComponent(root.graph(), "my_component")
    command.do()

    assert root.graph().components()

    command.undo()

    assert not root.graph().components()

    command.redo()

    assert root.graph().components()
