import json
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Dict, Optional

from orodruin.graph import Graph
from orodruin.library import (
    ComponentNotFoundError,
    Library,
    LibraryDoesNotExistError,
    LibraryManager,
)

from ...component import Component
from ...port import PortDirection
from ...port import types as port_types
from .. import Command, CreateComponent, CreatePort


@dataclass
class ImportComponent(Command):
    graph: Graph
    component_name: str
    library_name: str
    target_name: str = "orodruin"

    imported_component: Component = field(init=False)

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

        self.imported_component = self._component_from_json(
            self.graph,
            component_path,
            self.component_name,
        )

        return self.imported_component

    def undo(self) -> None:
        """Exporting a component is not undoable."""
        pass

    def _component_from_json(
        self,
        graph: Graph,
        component_path: PathLike,
        component_name: str
        # component_type: Optional[str] = None,
        # library: Optional[Library] = None,
        # parent: Optional[Component] = None,
    ) -> "Component":
        """Create a component from its json representation."""
        with open(component_path, "r", encoding="utf-8") as handle:
            component_data = json.loads(handle.read())

        return self._component_from_data(
            graph,
            component_data,
            component_name
            # component_type,
            # library,
            # parent,
        )

    def _component_from_data(
        self,
        graph: Graph,
        component_data: Dict[str, Any],
        component_name: str,
        component_type: Optional[str] = None,
        # library: Optional["Library"] = None,
        # parent: Optional[Component] = None,
    ) -> Component:
        """Create a component from its serialized data."""
        create_component_cmd = CreateComponent(
            graph=graph,
            name=component_name,
            type=None,
        )

        component = create_component_cmd.do()

        self._create_ports(graph, component, component_data["ports"])

        # ComponentDeserializer._create_subcomponents(
        #     component,
        #     component_data["components"],
        #     component_data["definitions"],
        # )
        # ComponentDeserializer._create_connections(
        #     component,
        #     component_data["connections"],
        # )

        return component

    def _create_ports(
        self,
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
