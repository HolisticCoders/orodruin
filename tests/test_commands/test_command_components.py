# pylint: disable = missing-module-docstring, missing-function-docstring

from pathlib import Path

from orodruin.commands import CreateComponent, DeleteComponent, RenameComponent
from orodruin.core import Scene
from orodruin.core.library import Library


def test_create_component_init(scene: Scene) -> None:
    CreateComponent(scene, "my_component")
    CreateComponent(scene, "my_component", type="Multiply")
    CreateComponent(scene, "my_component", library=Library(Path("")))
    CreateComponent(scene, "my_component", graph=scene.root_graph())


def test_create_component_do_undo_redo(scene: Scene) -> None:
    assert not scene.root_graph().components()

    command = CreateComponent(scene, "my_component")
    command.do()

    assert scene.root_graph().components()


def test_delete_component_init(scene: Scene) -> None:
    component = CreateComponent(scene, "my_component").do()

    DeleteComponent(scene, component)
    DeleteComponent(scene, component.uuid())


def test_delete_component_do_undo_redo(scene: Scene) -> None:

    command = CreateComponent(scene, "my_component")
    component = command.do()

    assert scene.root_graph().components()

    command = DeleteComponent(scene, component)
    command.do()

    assert not scene.root_graph().components()

    # command.undo()

    # assert scene.root_graph().components()

    # command.redo()

    # assert not scene.root_graph().components()


def test_rename_component_init(scene: Scene) -> None:
    component = CreateComponent(scene, "initial_name").do()
    RenameComponent(component, "new_name")


def test_rename_component_do_undo_redo(scene: Scene) -> None:
    component = CreateComponent(scene, "initial_name").do()

    command = RenameComponent(component, "new_name")

    assert component.name() == "initial_name"

    command.do()

    assert component.name() == "new_name"

    command.undo()

    assert component.name() == "initial_name"

    command.redo()

    assert component.name() == "new_name"


def test_rename_component_same_name(scene: Scene) -> None:
    component_name = "my_component"
    component = CreateComponent(scene, component_name).do()

    command = RenameComponent(component, component_name)

    assert component.name() == component_name

    command.do()

    assert component.name() == component_name

    command.undo()

    assert component.name() == component_name

    command.redo()

    assert component.name() == component_name
