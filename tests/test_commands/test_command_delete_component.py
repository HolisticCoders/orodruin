# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin import Component
from orodruin.command.components import DeleteComponent


def test_create_component_init(root: Component) -> None:
    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    DeleteComponent(root.graph(), component.uuid())


def test_connect_port_do_undo_redo(root: Component) -> None:

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
