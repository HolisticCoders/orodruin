from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Command(Generic[T], metaclass=ABCMeta):

    """Encapsulate one or more undoable actions in a single command."""

    @abstractmethod
    def do(self) -> Any:
        """Perform the command actions."""

    @abstractmethod
    def undo(self) -> Any:
        """Undo the command actions."""

    def redo(self) -> Any:
        """Redo the command, after an undo."""
        self.do()
