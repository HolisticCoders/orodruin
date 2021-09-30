# pylint: disable = missing-module-docstring, missing-function-docstring

from pathlib import Path

from orodruin.commands import CreateNode, DeleteNode, RenameNode
from orodruin.core import State
from orodruin.core.library import Library


def test_create_node_init(state: State) -> None:
    CreateNode(state, "my_node")
    CreateNode(state, "my_node", type="Multiply")
    CreateNode(state, "my_node", library=Library(Path("")))
    CreateNode(state, "my_node", graph=state.root_graph())


def test_create_node_do_undo_redo(state: State) -> None:
    assert not state.root_graph().nodes()

    command = CreateNode(state, "my_node")
    command.do()

    assert state.root_graph().nodes()


def test_delete_node_init(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    DeleteNode(state, node)
    DeleteNode(state, node.uuid())


def test_delete_node_do_undo_redo(state: State) -> None:

    command = CreateNode(state, "my_node")
    node = command.do()

    assert state.nodes()
    assert state.root_graph().nodes()

    command = DeleteNode(state, node)
    command.do()

    assert not state.nodes()
    assert not state.root_graph().nodes()

    # command.undo()

    # assert state.root_graph().nodes()

    # command.redo()

    # assert not state.root_graph().nodes()


def test_rename_node_init(state: State) -> None:
    node = CreateNode(state, "initial_name").do()
    RenameNode(state, node, "new_name")


def test_rename_node_do_undo_redo(state: State) -> None:
    node = CreateNode(state, "initial_name").do()

    command = RenameNode(state, node, "new_name")

    assert node.name() == "initial_name"

    command.do()

    assert node.name() == "new_name"

    command.undo()

    assert node.name() == "initial_name"

    command.redo()

    assert node.name() == "new_name"


def test_rename_node_same_name(state: State) -> None:
    node_name = "my_node"
    node = CreateNode(state, node_name).do()

    command = RenameNode(state, node, node_name)

    assert node.name() == node_name

    command.do()

    assert node.name() == node_name

    command.undo()

    assert node.name() == node_name

    command.redo()

    assert node.name() == node_name
