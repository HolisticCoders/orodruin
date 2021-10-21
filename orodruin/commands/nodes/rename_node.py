"""Rename Node command."""
from __future__ import annotations
from typing import TYPE_CHECKING

import attr

from orodruin.core.utils import get_unique_node_name

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Node, NodeLike, State


@attr.s
class RenameNode(Command):
    """Rename Node command."""

    state: State = attr.ib()
    node: NodeLike = attr.ib()
    name: str = attr.ib()

    _node: Node = attr.ib(init=False)
    _old_name: str = attr.ib(init=False)
    _new_name: str = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._node = self.state.get_node(self.node)

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
