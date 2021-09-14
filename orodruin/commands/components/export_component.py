import json
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from orodruin.library import Library, LibraryDoesNotExistError, LibraryManager

from ...component import Component
from ...port import Port
from ..command import Command


@dataclass
class ExportComponent(Command):

    component: Component
    library_name: str
    target_name: str = "orodruin"
    component_name: Optional[str] = None

    exported_path: Path = field(init=False)

    def do(self) -> Path:
        library = LibraryManager.find_library(self.library_name)

        if not library:
            raise LibraryDoesNotExistError(
                f"Found no registered library called {self.library_name}"
            )

        if not self.component_name:
            self.component_name = self.component.name()

        self.exported_path = (
            library.path() / self.target_name / f"{self.component_name}.json"
        )

        with self.exported_path.open("w") as f:
            serialized_component = self._component_as_json(self.component)
            f.write(serialized_component)

        return self.exported_path

    def undo(self) -> None:
        """Exporting a component is not undoable."""
        pass

    @classmethod
    def _component_as_json(cls, component: Component) -> str:
        """Returns the serialized representation of the component."""
        return json.dumps(
            cls._component_definition_data(component),
            indent=4,
        )

    @classmethod
    def _component_definition_data(cls, component: Component) -> Dict[str, Any]:
        """Returns a dict representing the given Component definition.

        This is recursively called on all the subcomponents,
        returning a dict that represents the entire rig.
        """
        data = {
            "definitions": cls._sub_component_definitions(component),
            "components": cls._sub_component_instances(component),
            "ports": cls._serialize_ports(component),
            "connections": cls._component_connections(component),
        }
        return data

    @classmethod
    def _sub_component_definitions(cls, component: Component) -> Dict:
        definitions_data = {}

        for sub_component in component.graph().components():
            if sub_component.library():
                continue

            if sub_component.type() not in definitions_data:
                definition_data = cls._component_definition_data(sub_component)
                definitions_data[str(sub_component.type())] = definition_data

        return definitions_data

    @classmethod
    def _sub_component_instances(cls, component: Component) -> List:
        components_data = []

        for sub_component in component.graph().components():
            instance_data = cls._component_instance_data(sub_component)
            components_data.append(instance_data)

        return components_data

    @classmethod
    def _component_instance_data(cls, component: Component) -> Dict[str, Any]:
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

    @classmethod
    def _serialize_ports(cls, component: Component) -> List[Dict[str, str]]:
        ports_data = []

        for port in component.ports():
            ports_data.append(cls._port_definition_data(port))

        return ports_data

    @classmethod
    def _port_definition_data(cls, port: Port) -> Dict[str, str]:
        """Returns a dict representing the given Port definition."""
        data = {
            "name": port.name(),
            "direction": port.direction().name,
            "type": port.type().__name__,
        }
        return data

    @classmethod
    def _component_connections(cls, component: Component) -> List[Tuple[str, str]]:
        connection_data = []
        for connection in component.graph().connections():
            connection_data.append(
                (
                    str(connection.source().relative_path(component)),
                    str(connection.target().relative_path(component)),
                )
            )
        return connection_data
