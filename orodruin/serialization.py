from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from os import PathLike
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .component import Component
from .graph_manager import GraphManager
from .port import Port, PortDirection, SetConnectedPortError
from .port import types as port_types

if TYPE_CHECKING:
    from orodruin.library import Library  # pylint: disable=cyclic-import


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any) -> Any:
        if isinstance(o, PurePosixPath):
            return str(o)

        if is_dataclass(o):
            return asdict(o)

        return json.JSONEncoder.default(self, o)


class ComponentSerializer:
    """Methods handling Component Serialization."""

    def __init__(self) -> None:
        raise TypeError(f"Type {self.__class__.__name__} cannot be instantiated.")

    @staticmethod
    def component_as_json(component: Component, indent: int = 4) -> str:
        """Returns the serialized representation of the component."""
        return json.dumps(
            ComponentSerializer.component_definition_data(component),
            indent=indent,
            cls=OrodruinEncoder,
        )

    @staticmethod
    def component_definition_data(component: Component) -> Dict[str, Any]:
        """Returns a dict representing the given Component definition.

        This is recursively called on all the subcomponents,
        returning a dict that represents the entire rig.
        """
        data = {
            "definitions": ComponentSerializer._sub_component_definitions(component),
            "components": ComponentSerializer._sub_component_instances(component),
            "ports": ComponentSerializer._component_ports(component),
            "connections": ComponentSerializer._component_connections(component),
        }
        return data

    @staticmethod
    def component_instance_data(component: Component) -> Dict[str, Any]:
        """Return the data representation of the instanced component."""
        library = component.library

        if library is None:
            library_name = "Internal"
        else:
            library_name = library.name

        data = {
            "type": f"{library_name}::{component.type}",
            "name": component.name,
            "ports": {p.name: p.get() for p in component.ports},
        }
        return data

    @staticmethod
    def _port_definition_data(port: Port) -> Dict[str, Any]:
        """Returns a dict representing the given Port definition."""
        data = {
            "name": port.name,
            "direction": port.direction.name,
            "type": port.type.__name__,
        }
        return data

    @staticmethod
    def _sub_component_definitions(component: Component) -> Dict:
        definitions_data = {}

        for sub_component in component.components:
            sub_component_type = sub_component.type

            if sub_component.library is None:
                if sub_component_type not in definitions_data:
                    definition_data = ComponentSerializer.component_definition_data(
                        sub_component
                    )
                    definitions_data[str(sub_component_type)] = definition_data

        return definitions_data

    @staticmethod
    def _sub_component_instances(component: Component) -> List:
        components_data = []

        for sub_component in component.components:
            instance_data = ComponentSerializer.component_instance_data(sub_component)
            components_data.append(instance_data)

        return components_data

    @staticmethod
    def _component_ports(component: Component) -> List[Dict[str, Any]]:
        ports_data = []

        for port in component.ports:
            ports_data.append(ComponentSerializer._port_definition_data(port))

        return ports_data

    @staticmethod
    def _component_connections(
        component: Component,
    ) -> List[Tuple[PurePosixPath, PurePosixPath]]:
        connections_data = []

        for sub_component in component.components:
            for port in sub_component.ports:
                for connection in port.external_connections():
                    source = connection[0]
                    target = connection[1]
                    if source and target:
                        connection_paths = (
                            source.relative_path(relative_to=component),
                            target.relative_path(relative_to=component),
                        )
                        if connection_paths not in connections_data:
                            connections_data.append(connection_paths)

        return connections_data


class ComponentDeserializer:
    """Methods handling Component Deserialization."""

    def __init__(self) -> None:
        raise TypeError(f"Type {self.__class__.__name__} cannot be instantiated.")

    @staticmethod
    def component_from_json(
        file_path: PathLike,
        component_type: Optional[str] = None,
        library: Optional["Library"] = None,
        parent: Optional[Component] = None,
    ) -> "Component":
        """Create a component from its json representation."""
        with open(file_path, "r") as handle:
            data = json.loads(handle.read())

        return ComponentDeserializer.component_from_data(
            data,
            component_type,
            library,
            parent,
        )

    @staticmethod
    def component_from_data(
        component_data: Dict[str, Any],
        component_type: Optional[str] = None,
        library: Optional["Library"] = None,
        parent: Optional[Component] = None,
    ) -> Component:
        """Create a component from its serialized data."""

        component = Component.new(
            "root",
            component_type=component_type,
            library=library,
            parent=parent,
        )

        ComponentDeserializer._create_ports(component, component_data["ports"])
        ComponentDeserializer._create_subcomponents(
            component,
            component_data["components"],
            component_data["definitions"],
        )
        ComponentDeserializer._create_connections(
            component,
            component_data["connections"],
        )

        return component

    @staticmethod
    def _create_ports(component: Component, ports_data: Dict) -> None:
        for port_data in ports_data:
            name = port_data["name"]
            direction = PortDirection[port_data["direction"]]

            try:
                port_type = getattr(port_types, port_data["type"])
            except AttributeError as error:
                raise NameError(
                    f"Type {port_data['type']} is not registered as an "
                    "orodruin port type"
                ) from error

            component.add_port(name, direction, port_type)

    @staticmethod
    def _create_subcomponents(
        component: Component,
        subcomponents_data: Dict,
        internal_definitions: Dict,
    ) -> None:
        for sub_component_data in subcomponents_data:
            library, sub_component_type = sub_component_data["type"].split("::")
            sub_component_name = sub_component_data["name"]

            if library == "Internal":
                sub_component_definition = internal_definitions[sub_component_type]
                sub_component = ComponentDeserializer.component_from_data(
                    sub_component_definition,
                    sub_component_type,
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

    @staticmethod
    def _create_connections(
        component: Component,
        connections_data: List[Tuple[str, str]],
    ) -> None:
        for connection in connections_data:
            source = GraphManager.port_from_path(component, connection[0])
            target = GraphManager.port_from_path(component, connection[1])

            if source and target:
                source.connect(target)
