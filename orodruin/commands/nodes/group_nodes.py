"""Create Node command."""
from dataclasses import dataclass, field
from typing import List, Optional

from orodruin.core import Node, Graph, Library
from orodruin.core.utils import get_unique_name

from ..command import Command
from .create_node import CreateNode


@dataclass
class GroupNodes(Command):
    """Create Node command."""

    graph: Graph
    nodes: List[Node]

    _created_node: Node = field(init=False)
    _command_stack: List[Command] = field(default_factory=list)

    def do(self) -> Node:
        create_node_command = CreateNode(self.graph, "NewNode")
        self._command_stack.append(create_node_command)
        self._created_node = create_node_command.do()

        for node in self.nodes:
            self.graph.unregister_node(node.uuid())
            self._created_node.graph().register_node(node)

        return self._created_node

    def undo(self) -> None:
        # TODO: Delete all the connections from/to this node
        # TODO: Delete all the Ports from this node
        self.graph.unregister_node(self._created_node.uuid())

    def redo(self) -> None:
        # TODO: Delete all the Ports from this node
        # TODO: Recreate all the connections from/to this node
        self.graph.register_node(self._created_node)
