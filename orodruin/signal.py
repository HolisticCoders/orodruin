from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class Signal:

    _callbacks: List[Callable] = field(default_factory=list)

    def subscribe(self, callback: Callable):
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args, **kwargs) -> None:
        for callback in self._callbacks:
            callback(*args, **kwargs)
