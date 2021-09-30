# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import PurePosixPath

import pytest

from orodruin.core import Node, Port, PortDirection, State
from orodruin.core.pathed_object import PathedObject


def test_implements_pathed_object() -> None:
    issubclass(Node, PathedObject)


def test_init_node(state: State) -> None:
    assert len(state.nodes()) == 0

    node = state.create_node("node")

    assert len(state.nodes()) == 1
    assert node.name() == "node"


def test_add_ports(state: State) -> None:

    node = state.create_node("node")

    assert len(node.ports()) == 0

    input1 = state.create_port(
        "input1", PortDirection.input, int, node, state.root_graph()
    )
    input2 = state.create_port(
        "input2", PortDirection.input, int, node, state.root_graph()
    )
    output = state.create_port(
        "output", PortDirection.input, int, node, state.root_graph()
    )

    assert len(state.ports()) == 3

    node.register_port(input1)
    node.register_port(input2)
    node.register_port(output)

    assert len(node.ports()) == 3


def test_set_name(state: State) -> None:
    node = state.create_node("original_name")

    assert node.name() == "original_name"

    node.set_name("new_name")

    assert node.name() == "new_name"


def test_path_root_node(state: State) -> None:
    node = state.create_node("root")
    assert node.path() == PurePosixPath("/root")


def test_path_nested_node(state: State) -> None:
    root_node = state.create_node("root")
    child_a = state.create_node("child_a")
    child_b = state.create_node("child_b")

    child_a.set_parent_graph(root_node.graph().uuid())
    child_b.set_parent_graph(child_a.graph().uuid())

    assert child_b.path() == PurePosixPath("/root/child_a/child_b")


def test_path_nested_node_relative(state: State) -> None:
    root_node = state.create_node("root")
    child_a = state.create_node("child_a")
    child_b = state.create_node("child_b")

    child_a.set_parent_graph(root_node.graph())
    child_b.set_parent_graph(child_a.graph())

    assert child_b.relative_path(relative_to=child_a) == PurePosixPath("child_b")


def test_access_port(state: State) -> None:
    node = state.create_node("node")
    port = state.create_port(
        "input1", PortDirection.input, int, node, state.root_graph()
    )
    node.register_port(port)
    assert isinstance(node.port("input1"), Port)


def test_access_innexisting_port(state: State) -> None:
    node = state.create_node("node")
    with pytest.raises(NameError):
        node.port("this_is_not_a_port")
