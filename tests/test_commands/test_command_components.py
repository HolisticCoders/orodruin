# pylint: disable = missing-module-docstring, missing-function-docstring

from pathlib import Path

from orodruin.commands import CreateComponent, DeleteComponent, RenameComponent
from orodruin.core import State
from orodruin.core.library import Library


def test_create_component_init(state: State) -> None:
    CreateComponent(state, "my_component")
    CreateComponent(state, "my_component", type="Multiply")
    CreateComponent(state, "my_component", library=Library(Path("")))
    CreateComponent(state, "my_component", graph=state.root_graph())


def test_create_component_do_undo_redo(state: State) -> None:
    assert not state.root_graph().components()

    command = CreateComponent(state, "my_component")
    command.do()

    assert state.root_graph().components()


def test_delete_component_init(state: State) -> None:
    component = CreateComponent(state, "my_component").do()

    DeleteComponent(state, component)
    DeleteComponent(state, component.uuid())


def test_delete_component_do_undo_redo(state: State) -> None:

    command = CreateComponent(state, "my_component")
    component = command.do()

    assert state.root_graph().components()

    command = DeleteComponent(state, component)
    command.do()

    assert not state.root_graph().components()

    # command.undo()

    # assert state.root_graph().components()

    # command.redo()

    # assert not state.root_graph().components()


def test_rename_component_init(state: State) -> None:
    component = CreateComponent(state, "initial_name").do()
    RenameComponent(component, "new_name")


def test_rename_component_do_undo_redo(state: State) -> None:
    component = CreateComponent(state, "initial_name").do()

    command = RenameComponent(component, "new_name")

    assert component.name() == "initial_name"

    command.do()

    assert component.name() == "new_name"

    command.undo()

    assert component.name() == "initial_name"

    command.redo()

    assert component.name() == "new_name"


def test_rename_component_same_name(state: State) -> None:
    component_name = "my_component"
    component = CreateComponent(state, component_name).do()

    command = RenameComponent(component, component_name)

    assert component.name() == component_name

    command.do()

    assert component.name() == component_name

    command.undo()

    assert component.name() == component_name

    command.redo()

    assert component.name() == component_name
