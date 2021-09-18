from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Command(Generic[T], metaclass=ABCMeta):

    """Encapsulate one or more undoable actions in a single command."""

    @abstractmethod
    def do(self) -> Any:
        """Perform the command actions."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command actions."""

    def redo(self) -> None:
        """Redo the command, after an undo."""
        self.do()
