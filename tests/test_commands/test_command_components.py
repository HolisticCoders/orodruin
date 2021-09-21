# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreateComponent, DeleteComponent, RenameComponent
from orodruin.core import Component, Graph


def test_create_component_init(root_graph: Graph) -> None:
    CreateComponent(root_graph, "my_component")


def test_create_component_do_undo_redo(root_graph: Graph) -> None:
    assert not root_graph.components()

    command = CreateComponent(root_graph, "my_component")
    command.do()

    assert root_graph.components()

    command.undo()

    assert not root_graph.components()

    command.redo()

    assert root_graph.components()


def test_delete_component_init(root_graph: Graph) -> None:
    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    DeleteComponent(root_graph, component.uuid())


def test_delete_component_do_undo_redo(root_graph: Graph) -> None:

    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    assert root_graph.components()

    command = DeleteComponent(root_graph, component.uuid())
    command.do()

    assert not root_graph.components()

    command.undo()

    assert root_graph.components()

    command.redo()

    assert not root_graph.components()


def test_rename_component_init(root_graph: Graph) -> None:
    component = CreateComponent(root_graph, "initial_name").do()
    RenameComponent(component, "new_name")


def test_rename_component_do_undo_redo(root_graph: Graph) -> None:
    component = CreateComponent(root_graph, "initial_name").do()

    command = RenameComponent(component, "new_name")

    assert component.name() == "initial_name"

    command.do()

    assert component.name() == "new_name"

    command.undo()

    assert component.name() == "initial_name"

    command.redo()

    assert component.name() == "new_name"


def test_rename_component_same_name(root_graph: Graph) -> None:
    component_name = "my_component"
    component = CreateComponent(root_graph, component_name).do()

    command = RenameComponent(component, component_name)

    assert component.name() == component_name

    command.do()

    assert component.name() == component_name

    command.undo()

    assert component.name() == component_name

    command.redo()

    assert component.name() == component_name
