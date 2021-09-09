from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Signal:
    """Signal class used to notify clients of orodruin's state updates."""

    _callbacks: List[Callable] = field(default_factory=list)

    def subscribe(self, callback: Callable) -> None:
        """Add a new callback to be called when the signal is emited."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Remove the callbacks from the registered callbacks."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        """
        Emit the signal.

        This calls every registered callbacks and passes *args and **kwargs directly
        to them.
        """
        for callback in self._callbacks:
            callback(*args, **kwargs)
