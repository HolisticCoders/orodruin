"""Export Node command"""
import json
import re
from pathlib import Path
from typing import Optional

import attr

from orodruin.core import LibraryManager, Node
from orodruin.core.serializer import DefaultSerializer
from orodruin.exceptions import LibraryDoesNotExistError

from ..command import Command


@attr.s
class ExportNode(Command):
    """Export Node command"""

    node: Node = attr.ib()
    library_name: str = attr.ib()
    target_name: str = attr.ib(default="orodruin")
    node_name: Optional[str] = attr.ib(default=None)

    _exported_path: Path = attr.ib(init=False)

    def do(self) -> Path:
        library = LibraryManager.find_library(self.library_name)

        if not library:
            raise LibraryDoesNotExistError(
                f"Found no registered library called {self.library_name}"
            )

        if not self.node_name:
            self.node_name = self.node.name()

        self._exported_path = (
            library.path() / self.target_name / f"{self.node_name}2.json"
        )

        serializer = DefaultSerializer()
        data = serializer.serialize(self.node)

        with self._exported_path.open("w") as f:
            content = json.dumps(
                data,
                indent=2,
                separators=(",", ": "),
            )
            content = re.sub(r"\n\s+(\]|\-?\d)", r" \1", content)
            f.write(content)

        return self._exported_path

    def undo(self) -> None:
        """Command is not undoable."""
