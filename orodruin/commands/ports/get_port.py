"""Get Port command."""
from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from orodruin.core.port import PortType

from ..command import Command

if TYPE_CHECKING:
    from orodruin.core import Port


@attr.s
class GetPort(Command[PortType]):
    """Get Port command."""

    port: Port[PortType] = attr.ib()

    def do(self) -> PortType:
        return self.port.get()

    def undo(self) -> None:
        """Command is not undoable."""
