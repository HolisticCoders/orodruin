from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from os import PathLike
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, Dict, Optional

from .component import Component
from .graph_manager import GraphManager
from .port import Port, SetConnectedPortError
from .port import types as port_types

if TYPE_CHECKING:
    from orodruin.library import Library  # pylint: disable=cyclic-import


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any):
        if isinstance(o, PurePosixPath):
            return str(o)

        if is_dataclass(o):
            return asdict(o)

        return json.JSONEncoder.default(self, o)


def component_instance_data(component: Component) -> Dict[str, Any]:
    """Return the data representation of the instanced component."""
    library = component.library

    if library is not None:
        library = library.name
    else:
        library = "Internal"

    data = {
        "type": f"{library}::{component.type}",
        "name": component.name,
        "ports": {p.name: p.get() for p in component.ports},
    }
    return data


def port_definition_data(port: Port) -> Dict[str, Any]:
    """Returns a dict representing the given Port definition."""
    data = {
        "name": port.name,
        "direction": port.direction.name,
        "type": port.type.__name__,
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
    for sub_component in component.components:
        sub_component_type = sub_component.type

        if sub_component.library is None:
            if sub_component_type not in definitions:
                definition_data = component_definition_data(sub_component)
                definitions[str(sub_component_type)] = definition_data
    data["definitions"] = definitions

    # register sub component instances
    components = []
    for sub_component in component.components:
        instance_data = component_instance_data(sub_component)
        components.append(instance_data)
    data["components"] = components

    ports = []
    for port in component.ports:
        ports.append(port_definition_data(port))
    data["ports"] = ports

    connections = []
    for sub_component in component.components:
        for port in sub_component.ports:
            for connection in port.external_connections():
                source = connection[0]
                target = connection[1]
                if source and target:
                    connection = (
                        source.relative_path(relative_to=component),
                        target.relative_path(relative_to=component),
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


def component_from_json(
    file_path: PathLike,
    component_type: Optional[str] = None,
    library: Optional["Library"] = None,
    parent: Optional[Component] = None,
) -> "Component":
    """Create a component from its json representation."""
    with open(file_path, "r") as handle:
        data = json.loads(handle.read())

    return component_from_data(data, component_type, library, parent)


def component_from_data(
    component_data,
    component_type: Optional[str] = None,
    library: Optional["Library"] = None,
    parent: Optional[Component] = None,
):  # pylint: disable = too-many-locals
    """Create a component from its serialized data."""

    component = Component.new(
        "root",
        component_type=component_type,
        library=library,
        parent=parent,
    )

    for port_data in component_data["ports"]:
        name = port_data["name"]
        direction = Port.Direction[port_data["direction"]]

        try:
            port_type = getattr(port_types, port_data["type"])
        except AttributeError as error:
            raise NameError(
                f"Type {port_data['type']} is not registered as an "
                "orodruin port type"
            ) from error

        component.add_port(name, direction, port_type)

    components = component_data["components"]
    definitions = component_data["definitions"]
    for sub_component_data in components:
        sub_component_type = sub_component_data["type"]
        sub_component_name = sub_component_data["name"]

        if sub_component_type.startswith("Internal"):
            type_uuid = sub_component_type.split("::")[-1]
            sub_component_definition = definitions[type_uuid]
            sub_component = component_from_data(
                sub_component_definition,
                type_uuid,
            )
        else:

            from .library import (  # pylint: disable = import-outside-toplevel, cyclic-import
                LibraryManager,
            )

            sub_component = LibraryManager.get_component(sub_component_type)

        sub_component.name = sub_component_name
        sub_component.parent = component

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
