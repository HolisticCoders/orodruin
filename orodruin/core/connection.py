from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .port import Port
    from .state import State


@dataclass
class Connection:
    """Orodruin's port Connection Class."""

    _state: State

    _source_id: UUID
    _target_id: UUID

    _uuid: UUID = field(default_factory=uuid4)

    def uuid(self) -> UUID:
        """UUID of this connection."""
        return self._uuid

    def source(self) -> Port:
        """Return the source port of this connection."""
        return self._state.port_from_portlike(self._source_id)

    def target(self) -> Port:
        """Return the target port of this connection."""
        return self._state.port_from_portlike(self._target_id)


ConnectionLike = Union[Connection, UUID]

__all__ = [
    "Connection",
    "ConnectionLike",
]
