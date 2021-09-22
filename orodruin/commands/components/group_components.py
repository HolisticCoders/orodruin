"""Create Component command."""
from dataclasses import dataclass, field
from typing import List, Optional

from orodruin.core import Component, Graph, Library
from orodruin.core.utils import get_unique_name

from ..command import Command
from .create_component import CreateComponent


@dataclass
class GroupComponents(Command):
    """Create Component command."""

    graph: Graph
    components: List[Component]

    _created_component: Component = field(init=False)
    _command_stack: List[Command] = field(default_factory=list)

    def do(self) -> Component:
        create_component_command = CreateComponent(self.graph, "NewComponent")
        self._command_stack.append(create_component_command)
        self._created_component = create_component_command.do()

        for component in self.components:
            self.graph.unregister_component(component.uuid())
            self._created_component.graph().register_component(component)

        return self._created_component

    def undo(self) -> None:
        # TODO: Delete all the connections from/to this component
        # TODO: Delete all the Ports from this component
        self.graph.unregister_component(self._created_component.uuid())

    def redo(self) -> None:
        # TODO: Delete all the Ports from this component
        # TODO: Recreate all the connections from/to this component
        self.graph.register_component(self._created_component)
