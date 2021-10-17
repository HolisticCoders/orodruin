from __future__ import annotations

from typing import TYPE_CHECKING, Union
from uuid import UUID, uuid4

import attr

if TYPE_CHECKING:
    from .graph import Graph
    from .port import Port
    from .state import State


@attr.s
class Connection:
    """Orodruin's port Connection Class."""

    _state: State = attr.ib()
    _graph_id: UUID = attr.ib()
    _source_id: UUID = attr.ib()
    _target_id: UUID = attr.ib()

    _uuid: UUID = attr.ib(factory=uuid4)

    def uuid(self) -> UUID:
        """UUID of this connection."""
        return self._uuid

    def graph(self) -> Graph:
        """Return the graph this connection exists in."""
        return self._state.get_graph(self._graph_id)

    def source(self) -> Port:
        """Return the source port of this connection."""
        return self._state.get_port(self._source_id)

    def target(self) -> Port:
        """Return the target port of this connection."""
        return self._state.get_port(self._target_id)


ConnectionLike = Union[Connection, UUID]

__all__ = [
    "Connection",
    "ConnectionLike",
]
