"""Serialization and Deserialization of Components."""
import json
from os import PathLike
from pathlib import PurePosixPath
from typing import Any, Dict

from orodruin.port import PortType

from .component import Component
from .graph_manager import GraphManager


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any):
        if isinstance(o, PurePosixPath):
            # if the obj is uuid, we simply return the value of uuid
            return str(o)
        return json.JSONEncoder.default(self, o)


def component_as_json(component, indent: int = 4):
    """Returns the serialized representation of the component."""
    return json.dumps(component.as_dict(), indent=indent, cls=OrodruinEncoder)


def component_from_json(file_path: PathLike):
    """Create a component from its json representation."""
    with open(file_path, "r") as handle:
        data = json.loads(handle.read())

    return component_from_data(data)


def component_from_data(component_data):
    """Create a component from its serialized data."""
    component = Component(component_data["name"])
    for port_data in component_data["ports"]:
        port_from_data(component, port_data)

    for sub_component_data in component_data["components"]:
        sub_component = component_from_data(sub_component_data)
        sub_component.set_parent(component)

    for connection in component_data["connections"]:
        source = GraphManager.port_from_path(component, connection[0])
        target = GraphManager.port_from_path(component, connection[1])
        source.connect(target)

    return component


def port_from_data(component: Component, port_data: Dict[str, Any]):
    """Create a port from its serialized data."""
    name = port_data["name"]
    port_type = PortType[port_data["type"]]
    value = port_data["value"]
    component.add_port(name, port_type)
    component.port(name).set(value)
