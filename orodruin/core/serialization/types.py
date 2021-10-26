"""Serialization types."""
from enum import Enum


class SerializationType(Enum):
    """Describe possible serialization types."""

    instance = "instance"
    definition = "definition"
