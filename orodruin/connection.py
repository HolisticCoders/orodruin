from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .port import Port


@dataclass
class Connection:
    """Orodruin's port Connection Class."""

    _source: Port
    _target: Port

    _uuid: UUID = field(default_factory=uuid4)

    def uuid(self) -> UUID:
        """UUID of this connection."""
        return self._uuid

    def source(self) -> Port:
        """Return the source port of this connection."""
        return self._source

    def target(self) -> Port:
        """Return the target port of this connection."""
        return self._target
