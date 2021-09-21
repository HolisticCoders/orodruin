# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreatePort, DeletePort
from orodruin.core import Component, Graph, PortDirection


def test_create_component_init(root_graph: Graph) -> None:
    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    CreatePort(root_graph, component, "my_port", PortDirection.input, int)


def test_connect_port_do_undo_redo(root_graph: Graph) -> None:

    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    assert not root_graph.ports()
    assert not component.ports()

    command = CreatePort(root_graph, component, "my_port", PortDirection.input, int)
    command.do()

    assert root_graph.ports()
    assert component.ports()

    command.undo()

    assert not root_graph.ports()
    assert not component.ports()

    command.redo()

    assert root_graph.ports()
    assert component.ports()


def test_delete_port_init(root_graph: Graph) -> None:
    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    port = CreatePort(root_graph, component, "my_port", PortDirection.input, int).do()

    DeletePort(root_graph, port.uuid())


def test_delete_port_do_undo_redo(root_graph: Graph) -> None:
    component = Component("my_component", _parent_graph=root_graph)
    root_graph.register_component(component)

    port = CreatePort(root_graph, component, "my_port", PortDirection.input, int).do()

    assert root_graph.ports()
    assert component.ports()

    command = DeletePort(root_graph, port.uuid())
    command.do()

    assert not root_graph.ports()
    assert not component.ports()

    command.undo()

    assert root_graph.ports()
    assert component.ports()

    command.redo()

    assert not root_graph.ports()
    assert not component.ports()
