from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Union

from ..component import Component
from ..library import LibraryManager
from ..serialization import ComponentSerializer
from .command import Command


@dataclass
class ExportComponent(Command):
    component: Component
    path: Union[str, PathLike]

    def do(self) -> None:
        self.path = Path(self.path)

        with self.path.open("w") as f:
            serialized_component = ComponentSerializer.component_as_json(self.component)
            f.write(serialized_component)

    def undo(self) -> None:
        """Exporting a component is not undoable."""
        pass
