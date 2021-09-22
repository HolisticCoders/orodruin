# pylint: disable = missing-module-docstring, missing-function-docstring

from orodruin.commands import CreateComponent, CreatePort, DeletePort
from orodruin.core import PortDirection
from orodruin.core.scene import Scene


def test_create_port_init(scene: Scene) -> None:
    component = CreateComponent(scene, "my_component").do()

    CreatePort(scene, component, "my_port", PortDirection.input, int)


def test_connect_port_do_undo_redo(scene: Scene) -> None:

    component = CreateComponent(scene, "my_component").do()

    assert not scene.ports()
    assert not scene.root_graph().ports()
    assert not component.ports()

    command = CreatePort(scene, component, "my_port", PortDirection.input, int)
    command.do()

    assert scene.ports()
    assert scene.root_graph().ports()
    assert component.ports()

    # command.undo()

    # assert not scene.ports()
    # assert not scene.root_graph().ports()
    # assert not component.ports()

    # command.redo()

    # assert scene.ports()
    # assert scene.root_graph().ports()
    # assert component.ports()


def test_delete_port_init(scene: Scene) -> None:
    component = CreateComponent(scene, "my_component").do()

    port = CreatePort(scene, component, "my_port", PortDirection.input, int).do()

    DeletePort(scene, port)
    DeletePort(scene, port.uuid())


def test_delete_port_do_undo_redo(scene: Scene) -> None:
    component = CreateComponent(scene, "my_component").do()

    port = CreatePort(scene, component, "my_port", PortDirection.input, int).do()

    assert scene.ports()
    assert scene.root_graph().ports()
    assert component.ports()

    command = DeletePort(scene, port)
    command.do()

    assert not scene.ports()
    assert not scene.root_graph().ports()
    assert not component.ports()

    # command.undo()

    # assert scene.ports()
    # assert scene.root_graph().ports()
    # assert component.ports()

    # command.redo()

    # assert not scene.ports()
    # assert not scene.root_graph().ports()
    # assert not component.ports()
