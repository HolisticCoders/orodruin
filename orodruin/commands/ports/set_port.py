"""Set Port command."""
from dataclasses import dataclass, field
from typing import TypeVar

from orodruin.core import Port

from ..command import Command

T = TypeVar("T")


@dataclass
class SetPort(Command[T]):
    """Set Port command."""

    port: Port[T]
    value: T

    _previous_value: T = field(init=False)

    def do(self) -> None:
        self._previous_value = self.port.get()
        self.port.set(self.value)

    def undo(self) -> None:
        self.port.set(self._previous_value)
