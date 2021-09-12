import json
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple

from orodruin.port.port import Port

from .component import Component


class ComponentSerializer:
    """Methods handling Component Serialization."""

    def __init__(self) -> None:
        raise NotImplementedError(
            f"Type {self.__class__.__name__} cannot be instantiated."
        )

    @staticmethod
    def component_as_json(component: Component, indent: int = 4) -> str:
        """Returns the serialized representation of the component."""
        return json.dumps(
            ComponentSerializer.component_definition_data(component),
            indent=indent,
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
            "ports": ComponentSerializer._serialize_ports(component),
            "connections": ComponentSerializer._component_connections(component),
        }
        return data

    @staticmethod
    def _sub_component_definitions(component: Component) -> Dict:
        definitions_data = {}

        for sub_component in component.graph().components():
            if sub_component.library():
                continue

            if sub_component.type() not in definitions_data:
                definition_data = ComponentSerializer.component_definition_data(
                    sub_component
                )
                definitions_data[str(sub_component.type())] = definition_data

        return definitions_data

    @staticmethod
    def _sub_component_instances(component: Component) -> List:
        components_data = []

        for sub_component in component.graph().components():
            instance_data = ComponentSerializer.component_instance_data(sub_component)
            components_data.append(instance_data)

        return components_data

    @staticmethod
    def component_instance_data(component: Component) -> Dict[str, Any]:
        """Return the data representation of the instanced component."""
        library = component.library()

        if library is None:
            library_name = "Internal"
        else:
            library_name = library.name()

        data = {
            "type": f"{library_name}::{component.type()}",
            "name": component.name(),
            "ports": {p.name(): p.get() for p in component.ports()},
        }
        return data

    @staticmethod
    def _serialize_ports(component: Component) -> List[Dict[str, str]]:
        ports_data = []

        for port in component.ports():
            ports_data.append(ComponentSerializer._port_definition_data(port))

        return ports_data

    @staticmethod
    def _port_definition_data(port: Port) -> Dict[str, str]:
        """Returns a dict representing the given Port definition."""
        data = {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
        }
        return data

    @staticmethod
    def _component_connections(component: Component) -> List[Tuple[str, str]]:
        connection_data = []
        for connection in component.graph().connections():
            connection_data.append(
                (
                    str(connection.source().relative_path(component)),
                    str(connection.target().relative_path(component)),
                )
            )
        return connection_data
