# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreateComponent, DeleteComponent, RenameComponent
from orodruin.core import Component


def test_create_component_init(root: Component) -> None:
    CreateComponent(root.graph(), "my_component")


def test_create_component_do_undo_redo(root: Component) -> None:
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


def test_rename_component_init(root: Component) -> None:
    component = CreateComponent(root.graph(), "initial_name").do()
    RenameComponent(component, "new_name")


def test_rename_component_do_undo_redo(root: Component) -> None:
    component = CreateComponent(root.graph(), "initial_name").do()

    command = RenameComponent(component, "new_name")

    assert component.name() == "initial_name"

    command.do()

    assert component.name() == "new_name"

    command.undo()

    assert component.name() == "initial_name"

    command.redo()

    assert component.name() == "new_name"
