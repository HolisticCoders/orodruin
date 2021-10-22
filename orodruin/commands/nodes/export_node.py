"""Export Node command"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import attr

from orodruin.core.library import LibraryManager
from orodruin.exceptions import LibraryDoesNotExistError

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Node, State


@attr.s
class ExportNode(Command):
    """Export Node command"""

    state: State = attr.ib()
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
            library.path() / self.target_name / f"{self.node_name}.json"
        )

        data = self.state.serialize(self.node)

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
