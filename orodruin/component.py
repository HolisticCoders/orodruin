"""Orodruin's Component Class.

A component can be seen as both a node and a graph,
it has `Ports` to receive and pass Data through the graph
and can contain other Components as a subgraph
"""
import json
from json import encoder
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pathlib import PurePath, PurePosixPath

from orodruin.port import Port, PortSide


class ComponentError(Exception):
    """Generic Component Error"""


class ParentToSelfError(ComponentError):
    """Component parented to itself."""


class ComponentDoesNotExistError(ComponentError):
    """Component does not exist."""


class OrodruinEncoder(json.JSONEncoder):
    """JSON Encoder to serialize UUIDs properly."""

    def default(self, o: Any):
        if isinstance(o, PurePath):
            # if the obj is uuid, we simply return the value of uuid
            return str(o)
        return json.JSONEncoder.default(self, o)


class Component:
    """Orodruin's Component Class.

    A component can be seen as both a node and a graph,
    it has `Ports` to receive and pass Data through the graph
    and can contain other Components as a subgraph
    """

    _instances: Dict[UUID, "Component"] = {}

    def __init__(self, name: str, uuid: Optional[UUID] = None) -> None:
        self._name: str = name

        if uuid:
            self._uuid: UUID = uuid
        else:
            self._uuid: UUID = uuid4()

        Component._instances[self._uuid] = self

        self._inputs: List[Port] = []
        self._outputs: List[Port] = []

        self._components: List[Component] = []
        self._parent: Optional[Component] = None

    @staticmethod
    def from_uuid(uuid: UUID) -> "Component":
        """return an existing component instance from its uuid"""
        instance = Component._instances.get(uuid)
        if not instance:
            raise ComponentDoesNotExistError(
                f"Component with uuid {uuid} does not exist"
            )
        return instance

    @staticmethod
    def from_path(path: str) -> "Component":
        for instance in Component._instances.values():
            if path == str(instance.path()):
                return instance
        raise ComponentDoesNotExistError(f"Component with path {path} does not exist")

    def __getattr__(self, name: str) -> Optional[Port]:
        for port in self._inputs:
            if port.name() == name:
                return port

        for port in self._outputs:
            if port.name() == name:
                return port

        return None

    def build(self) -> None:
        """Build the inner Graph of this Component.

        This method should be overriden for any Component
        that needs a direct implementation in each DCC
        """
        raise NotImplementedError

    def publish(self) -> None:
        """Cleans up the Component to be ready for Animation."""
        raise NotImplementedError

    def add_port(self, name: str, port_side: PortSide):
        """Add a `Port` to this Component."""
        port = Port(name, self)

        if port_side == PortSide.input:
            self._inputs.append(port)
        elif port_side == PortSide.output:
            self._outputs.append(port)

    def name(self) -> str:
        """Name of the Component."""
        return self._name

    def set_name(self, name: str):
        """Set the name of the component."""
        self._name = name

    def path(self) -> PurePosixPath:
        if self._parent is None:
            path = PurePosixPath(f"/{self._name}")
        else:
            path = self._parent.path().joinpath(f"{self._name}")
        return path

    def uuid(self) -> UUID:
        return self._uuid

    def inputs(self):
        """Input Ports of the Component."""
        return self._inputs

    def outputs(self):
        """Output Ports of the Component."""
        return self._outputs

    def components(self):
        """Sub-components of the component."""
        return self._components

    def parent(self):
        """Parent of the component."""
        return self._parent

    def set_parent(self, other: "Component"):
        """Set the parent of the component."""
        if other is self:
            raise ParentToSelfError(f"Cannot parent {self._name} to itself")

        self._parent = other
        if self not in other.components():
            other._components.append(self)

    def as_dict(self) -> Dict[str, Any]:
        """Returns a dict representing the Component.

        This is recursively called on all the subcomponents,
        returning a dict that represents the entire rig.
        """
        data = {
            "name": self._name,
            "components": [c.as_dict() for c in self._components],
        }

        inputs = []
        for port in self._inputs:
            inputs.append(port.as_dict())
        data["inputs"] = inputs

        outputs = []
        for port in self._outputs:
            outputs.append(port.as_dict())
        data["outputs"] = outputs

        return data

    def as_json(self, indent: int = 2):
        """Returns the serialized representation of the rig."""
        return json.dumps(self.as_dict(), indent=indent, cls=OrodruinEncoder)
