"""Serialization and Deserialization of Components."""
import json
from os import PathLike
from pathlib import PurePosixPath
from typing import Any, Dict
from uuid import UUID

from .component import Component
from .graph_manager import GraphManager
from .library import get_component
from .port import Port, SetConnectedPortError


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any):
        if isinstance(o, PurePosixPath):
            return str(o)

        if isinstance(o, UUID):
            return str(o)

        return json.JSONEncoder.default(self, o)


def component_instance_data(component: Component) -> Dict[str, Any]:
    """Return the data representation of the instanced component."""
    library = component.library() or "Internal"
    data = {
        "type": f"{library}::{component.type()}",
        "name": component.name(),
        "ports": {p.name(): p.get() for p in component.ports()},
    }
    return data


def port_definition_data(port: Port) -> Dict[str, Any]:
    """Returns a dict representing the given Port definition."""
    data = {
        "name": port.name(),
        "direction": port.direction().name,
        "type": port.type().name,
    }
    return data


def component_definition_data(component: Component) -> Dict[str, Any]:
    """Returns a dict representing the given Component definition.

    This is recursively called on all the subcomponents,
    returning a dict that represents the entire rig.
    """
    data = {}

    # add the internally defined components definitions
    definitions = {}
    for sub_component in component.components():
        sub_component_type = sub_component.type()

        if isinstance(sub_component_type, UUID):
            if sub_component_type not in definitions:
                definition_data = component_definition_data(sub_component)
                definitions[str(sub_component_type)] = definition_data
    data["definitions"] = definitions

    # register sub component instances
    components = []
    for sub_component in component.components():
        instance_data = component_instance_data(sub_component)
        components.append(instance_data)
    data["components"] = components

    ports = []
    for port in component.ports():
        ports.append(port_definition_data(port))
    data["ports"] = ports

    connections = []
    for sub_component in component.components():
        for port in sub_component.ports():
            for connection in port.external_connections():
                source = connection[0]
                target = connection[1]
                if source and target:
                    connection = (
                        source.path(relative_to=component),
                        target.path(relative_to=component),
                    )
                    if connection not in connections:
                        connections.append(connection)

    data["connections"] = connections

    return data


def component_as_json(component, indent: int = 4):
    """Returns the serialized representation of the component."""
    return json.dumps(
        component_definition_data(component),
        indent=indent,
        cls=OrodruinEncoder,
    )


def component_from_json(file_path: PathLike) -> "Component":
    """Create a component from its json representation."""
    with open(file_path, "r") as handle:
        data = json.loads(handle.read())

    return component_from_data(data)


def component_from_data(component_data):  # pylint: disable = too-many-locals
    """Create a component from its serialized data."""

    component = Component("root")
    for port_data in component_data["ports"]:
        name = port_data["name"]
        direction = Port.Direction[port_data["direction"]]
        port_type = Port.Type[port_data["type"]]
        component.add_port(name, direction, port_type)

    components = component_data["components"]
    definitions = component_data["definitions"]
    for sub_component_data in components:
        sub_component_type = sub_component_data["type"]
        sub_component_name = sub_component_data["name"]

        if sub_component_type.startswith("Internal"):
            type_uuid = sub_component_type.split("::")[-1]
            sub_component_definition = definitions[type_uuid]
            sub_component = component_from_data(sub_component_definition)
        else:
            referenced_component_path = get_component(sub_component_type)
            sub_component = component_from_json(referenced_component_path)

        sub_component.set_parent(component)
        sub_component.set_name(sub_component_name)
        sub_component_library, sub_component_type = sub_component_type.split("::")
        sub_component.set_type(sub_component_type)
        sub_component.set_library(sub_component_library)

        for port_name, port_value in sub_component_data["ports"].items():
            try:
                sub_component.port(port_name).set(port_value)
            except SetConnectedPortError:
                pass

    for connection in component_data["connections"]:
        source = GraphManager.port_from_path(component, connection[0])
        target = GraphManager.port_from_path(component, connection[1])
        source.connect(target)

    return component
