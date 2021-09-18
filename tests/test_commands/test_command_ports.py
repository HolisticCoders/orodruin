# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreatePort, DeletePort
from orodruin.core import Component, PortDirection


def test_create_component_init(root: Component) -> None:
    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    CreatePort(root.graph(), component, "my_port", PortDirection.input, int)


def test_connect_port_do_undo_redo(root: Component) -> None:

    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    assert not root.graph().ports()
    assert not component.ports()

    command = CreatePort(root.graph(), component, "my_port", PortDirection.input, int)
    command.do()

    assert root.graph().ports()
    assert component.ports()

    command.undo()

    assert not root.graph().ports()
    assert not component.ports()

    command.redo()

    assert root.graph().ports()
    assert component.ports()


def test_delete_port_init(root: Component) -> None:
    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    port = CreatePort(root.graph(), component, "my_port", PortDirection.input, int).do()

    DeletePort(root.graph(), port.uuid())


def test_delete_port_do_undo_redo(root: Component) -> None:
    component = Component("my_component", _parent_graph=root.graph())
    root.graph().register_component(component)

    port = CreatePort(root.graph(), component, "my_port", PortDirection.input, int).do()

    assert root.graph().ports()
    assert component.ports()

    command = DeletePort(root.graph(), port.uuid())
    command.do()

    assert not root.graph().ports()
    assert not component.ports()

    command.undo()

    assert root.graph().ports()
    assert component.ports()

    command.redo()

    assert not root.graph().ports()
    assert not component.ports()
