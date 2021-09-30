"""Rename Node command."""
from dataclasses import dataclass, field

from orodruin.core import Node
from orodruin.core.node import NodeLike
from orodruin.core.state import State
from orodruin.core.utils import get_unique_node_name

from ..command import Command


@dataclass
class RenameNode(Command):
    """Rename Node command."""

    state: State
    node: NodeLike
    name: str

    _node: Node = field(init=False)
    _old_name: str = field(init=False)
    _new_name: str = field(init=False)

    def __post_init__(self) -> None:
        self._node = self.state.node_from_nodelike(self.node)

    def do(self) -> str:
        self._old_name = self._node.name()

        if self.name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            self._new_name = self._old_name
            return self._old_name

        parent_graph = self._node.parent_graph()

        if parent_graph:
            self._new_name = get_unique_node_name(parent_graph, self.name)
        else:
            # The node isn't in a graph,
            # the new name can't clash with any other name.
            self._new_name = self.name

        self._node.set_name(self._new_name)

        return self._new_name

    def undo(self) -> None:
        if self._new_name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            return

        self._node.set_name(self._old_name)

    def redo(self) -> None:
        if self._new_name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            return

        self._node.set_name(self._new_name)
