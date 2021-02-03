"""Serialization and Deserialization of Components."""
import json
from pathlib import PurePosixPath
from typing import Any


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any):
        if isinstance(o, PurePosixPath):
            # if the obj is uuid, we simply return the value of uuid
            return str(o)
        return json.JSONEncoder.default(self, o)


def component_as_json(component, indent: int = 2):
    """Returns the serialized representation of the component."""
    return json.dumps(component.as_dict(), indent=indent, cls=OrodruinEncoder)
