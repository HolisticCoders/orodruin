import json
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from orodruin.library import Library

from ..component import Component
from ..port import Port
from .command import Command


@dataclass
class ExportComponent(Command):
    component: Component
    library: Union[str, PathLike, Library]
    path: Union[str, PathLike]

    def do(self) -> None:
        self.path = Path(self.path)

        with self.path.open("w") as f:
            serialized_component = self._component_as_json()
            f.write(serialized_component)

    def undo(self) -> None:
        """Exporting a component is not undoable."""
        pass

    def _component_as_json(self) -> str:
        """Returns the serialized representation of the component."""
        return json.dumps(
            self._component_definition_data(self.component),
            indent=4,
        )

    def _component_definition_data(self, component: Component) -> Dict[str, Any]:
        """Returns a dict representing the given Component definition.

        This is recursively called on all the subcomponents,
        returning a dict that represents the entire rig.
        """
        data = {
            "definitions": self._sub_component_definitions(component),
            "components": self._sub_component_instances(component),
            "ports": self._serialize_ports(component),
            "connections": self._component_connections(component),
        }
        return data

    def _sub_component_definitions(self, component: Component) -> Dict:
        definitions_data = {}

        for sub_component in component.graph().components():
            if sub_component.library():
                continue

            if sub_component.type() not in definitions_data:
                definition_data = self._component_definition_data(sub_component)
                definitions_data[str(sub_component.type())] = definition_data

        return definitions_data

    def _sub_component_instances(self, component: Component) -> List:
        components_data = []

        for sub_component in component.graph().components():
            instance_data = self._component_instance_data(sub_component)
            components_data.append(instance_data)

        return components_data

    def _component_instance_data(self, component: Component) -> Dict[str, Any]:
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

    def _serialize_ports(self, component: Component) -> List[Dict[str, str]]:
        ports_data = []

        for port in component.ports():
            ports_data.append(self._port_definition_data(port))

        return ports_data

    def _port_definition_data(self, port: Port) -> Dict[str, str]:
        """Returns a dict representing the given Port definition."""
        data = {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
        }
        return data

    def _component_connections(self, component: Component) -> List[Tuple[str, str]]:
        connection_data = []
        for connection in component.graph().connections():
            connection_data.append(
                (
                    str(connection.source().relative_path(component)),
                    str(connection.target().relative_path(component)),
                )
            )
        return connection_data
