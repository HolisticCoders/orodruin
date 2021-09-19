"""Import Component command."""
import json
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple

from orodruin.core import Component, Graph, Library, LibraryManager, PortDirection
from orodruin.core.port import types as port_types
from orodruin.core.utils import port_from_path
from orodruin.exceptions import (
    ComponentNotFoundError,
    LibraryDoesNotExistError,
    PortDoesNotExistError,
)

from ..command import Command
from ..ports import ConnectPorts, CreatePort, SetPort
from .create_component import CreateComponent


@dataclass
class ImportComponent(Command):
    """Import Component command."""

    graph: Graph
    component_name: str
    library_name: str
    target_name: str = "orodruin"

    _imported_component: Component = field(init=False)

    def do(self) -> Component:
        library = LibraryManager.find_library(self.library_name)

        if not library:
            raise LibraryDoesNotExistError(
                f"Found no registered library called {self.library_name}"
            )

        component_path = library.find_component(self.component_name, self.target_name)

        if not component_path:
            raise ComponentNotFoundError(
                f"Found no component in library {self.library_name} "
                f"for target {self.target_name}"
            )

        self._imported_component = self._component_from_json(
            self.graph,
            component_path,
            self.component_name,
            self.component_name,
            library,
        )

        return self._imported_component

    def undo(self) -> None:
        """Command is not undoable."""

    @classmethod
    def _component_from_json(
        cls,
        graph: Graph,
        component_path: PathLike,
        component_name: str,
        component_type: Optional[str] = None,
        library: Optional[Library] = None,
    ) -> "Component":
        """Create a component from its json representation."""
        with open(component_path, "r", encoding="utf-8") as handle:
            component_data = json.loads(handle.read())

        return cls._component_from_data(
            graph,
            component_data,
            component_name,
            component_type,
            library,
        )

    @classmethod
    def _component_from_data(
        cls,
        graph: Graph,
        component_data: Dict[str, Any],
        component_name: str,
        component_type: Optional[str] = None,
        library: Optional[Library] = None,
    ) -> Component:
        """Create a component from its serialized data."""
        component = CreateComponent(
            graph=graph,
            name=component_name,
            type=component_type,
            library=library,
        ).do()

        cls._create_ports(graph, component, component_data["ports"])

        cls._create_subcomponents(
            component,
            component_data["components"],
            component_data["definitions"],
        )
        cls._create_connections(
            component,
            component_data["connections"],
        )

        return component

    @classmethod
    def _create_ports(
        cls,
        graph: Graph,
        component: Component,
        ports_data: Dict,
    ) -> None:
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

            CreatePort(graph, component, name, direction, port_type).do()

    @classmethod
    def _create_subcomponents(
        cls,
        component: Component,
        subcomponents_data: Dict,
        internal_definitions: Dict,
    ) -> None:
        for subcomponent_data in subcomponents_data:
            library_name, subcomponent_type = subcomponent_data["type"].split("::")
            subcomponent_name = subcomponent_data["name"]

            if library_name == "Internal":
                subcomponent_definition = internal_definitions[subcomponent_type]
                sub_component = cls._component_from_data(
                    component.graph(),
                    subcomponent_definition,
                    subcomponent_name,
                    subcomponent_type,
                )
            else:
                sub_component = ImportComponent(
                    component.graph(),
                    subcomponent_type,
                    library_name,
                ).do()
                sub_component.set_name(subcomponent_name)

            for port_name, port_value in subcomponent_data["ports"].items():
                SetPort(sub_component.port(port_name), port_value).do()

    @classmethod
    def _create_connections(
        cls,
        component: Component,
        connections_data: List[Tuple[str, str]],
    ) -> None:

        for connection in connections_data:
            source_name = connection[0]
            target_name = connection[1]

            source_port = port_from_path(component, source_name)
            target_port = port_from_path(component, target_name)

            if not source_port:
                raise PortDoesNotExistError(f"Port {source_name} not found")
            if not target_port:
                raise PortDoesNotExistError(f"Port {target_name} not found")

            ConnectPorts(component.graph(), source_port, target_port).do()
