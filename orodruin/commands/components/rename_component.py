"""Rename Component command."""
from dataclasses import dataclass, field

from orodruin.core import Component
from orodruin.core.utils import get_unique_name

from ..command import Command


@dataclass
class RenameComponent(Command):
    """Rename Component command."""

    component: Component
    name: str

    _old_name: str = field(init=False)
    _new_name: str = field(init=False)

    def do(self) -> str:
        self._old_name = self.component.name()

        if self.name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            self._new_name = self._old_name
            return self._old_name

        parent_graph = self.component.parent_graph()

        if parent_graph:
            self._new_name = get_unique_name(parent_graph, self.name)
        else:
            # The component isn't in a graph,
            # the new name can't clash with any other name.
            self._new_name = self.name

        self.component.set_name(self._new_name)

        return self._new_name

    def undo(self) -> None:
        if self._new_name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            return

        self.component.set_name(self._old_name)

    def redo(self) -> None:
        if self._new_name == self._old_name:
            # Don't rename the node to avoid emiting the name_changed signal
            return

        self.component.set_name(self._new_name)
