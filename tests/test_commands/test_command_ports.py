# pylint: disable = missing-module-docstring, missing-function-docstring

from attr import asdict

from orodruin.commands import (
    CreateNode,
    CreatePort,
    DeletePort,
    GetPort,
    RenamePort,
    SetPort,
)
from orodruin.core import PortDirection
from orodruin.core.state import State


def test_create_port_init(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    CreatePort(state, node, "my_port", PortDirection.input, int)


def test_connect_port_do_undo_redo(state: State) -> None:

    node = CreateNode(state, "my_node").do()

    assert not state.ports()
    assert not state.root_graph().ports()
    assert not node.ports()

    command = CreatePort(state, node, "my_port", PortDirection.input, int)
    command.do()

    assert state.ports()
    assert state.root_graph().ports()
    assert node.ports()

    # command.undo()

    # assert not state.ports()
    # assert not state.root_graph().ports()
    # assert not node.ports()

    # command.redo()

    # assert state.ports()
    # assert state.root_graph().ports()
    # assert node.ports()


def test_delete_port_init(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    port = CreatePort(state, node, "my_port", PortDirection.input, int).do()

    DeletePort(state, port)
    DeletePort(state, port.uuid())


def test_delete_port_do_undo_redo(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    port = CreatePort(state, node, "my_port", PortDirection.input, int).do()

    assert state.ports()
    assert state.root_graph().ports()
    assert node.ports()

    command = DeletePort(state, port)
    command.do()

    assert not state.ports()
    assert not state.root_graph().ports()
    assert not node.ports()

    # command.undo()

    # assert state.ports()
    # assert state.root_graph().ports()
    # assert node.ports()

    # command.redo()

    # assert not state.ports()
    # assert not state.root_graph().ports()
    # assert not node.ports()


def test_get_port_do_undo_redo(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    port = CreatePort(state, node, "my_port", PortDirection.input, int).do()

    assert GetPort(port).do() == 0


def test_set_port_do_undo_redo(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    port = CreatePort(state, node, "my_port", PortDirection.input, int).do()

    assert GetPort(port).do() == 0

    SetPort(port, 42).do()

    assert GetPort(port).do() == 42


def test_rename_port_do_undo_redo(state: State) -> None:
    node = CreateNode(state, "my_node").do()

    port_name = "my_port"
    port = CreatePort(state, node, port_name, PortDirection.input, int).do()

    assert port.name() == port_name

    new_name = "new_port_name"
    RenamePort(state, port, new_name).do()

    assert port.name() == new_name
