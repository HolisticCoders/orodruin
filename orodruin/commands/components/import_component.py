import json
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from orodruin.library import Library

from ...component import Component
from ...port import Port
from ..command import Command


@dataclass
class ImportComponent(Command):
    component_name: str
    library: str

    def do(self) -> None:
        pass

    def undo(self) -> None:
        """Exporting a component is not undoable."""
        pass
