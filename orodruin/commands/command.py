from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):
    """Encapsulate one or more undoable actions in a single command."""

    @abstractmethod
    def do(self) -> None:
        """Perform the command actions."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command actions."""

    def redo(self) -> None:
        """Redo the command, after an undo."""
        self.do()
