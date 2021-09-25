# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreateComponent, CreatePort, DeletePort
from orodruin.core import PortDirection
from orodruin.core.state import State


def test_create_port_init(state: State) -> None:
    component = CreateComponent(state, "my_component").do()

    CreatePort(state, component, "my_port", PortDirection.input, int)


def test_connect_port_do_undo_redo(state: State) -> None:

    component = CreateComponent(state, "my_component").do()

    assert not state.ports()
    assert not state.root_graph().ports()
    assert not component.ports()

    command = CreatePort(state, component, "my_port", PortDirection.input, int)
    command.do()

    assert state.ports()
    assert state.root_graph().ports()
    assert component.ports()

    # command.undo()

    # assert not state.ports()
    # assert not state.root_graph().ports()
    # assert not component.ports()

    # command.redo()

    # assert state.ports()
    # assert state.root_graph().ports()
    # assert component.ports()


def test_delete_port_init(state: State) -> None:
    component = CreateComponent(state, "my_component").do()

    port = CreatePort(state, component, "my_port", PortDirection.input, int).do()

    DeletePort(state, port)
    DeletePort(state, port.uuid())


def test_delete_port_do_undo_redo(state: State) -> None:
    component = CreateComponent(state, "my_component").do()

    port = CreatePort(state, component, "my_port", PortDirection.input, int).do()

    assert state.ports()
    assert state.root_graph().ports()
    assert component.ports()

    command = DeletePort(state, port)
    command.do()

    assert not state.ports()
    assert not state.root_graph().ports()
    assert not component.ports()

    # command.undo()

    # assert state.ports()
    # assert state.root_graph().ports()
    # assert component.ports()

    # command.redo()

    # assert not state.ports()
    # assert not state.root_graph().ports()
    # assert not component.ports()
