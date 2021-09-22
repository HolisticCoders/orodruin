from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Generic, Type, TypeVar, Union
from uuid import UUID, uuid4

from orodruin.core.graph import Graph

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import
    from ..scene import Scene


class PortDirection(Enum):
    """Directions a port can have."""

    input = "input"
    output = "output"


PortType = TypeVar("PortType")  # pylint: disable = invalid-name


@dataclass
class Port(Generic[PortType]):
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    _scene: Scene
    _graph_id: UUID
    _component_id: UUID

    _name: str
    _direction: PortDirection
    _type: Type[PortType]

    _value: PortType = field(init=False)

    _uuid: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self._value = self._type()

    def scene(self) -> Scene:
        """Return the scene that owns this port."""
        return self._scene

    def graph(self) -> Graph:
        """Return the graph that this port exists in."""
        return self._scene.graph_from_uuid(self._graph_id)

    def component(self) -> Component:
        """The Component this Port is attached on."""
        return self._scene.component_from_uuid(self._component_id)

    def uuid(self) -> UUID:
        """UUID of this port."""
        return self._uuid

    def name(self) -> str:
        """Name of the port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the port."""
        self._name = name

    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    def type(self) -> Type[PortType]:
        """Type of the port."""
        return self._type

    def get(self) -> PortType:
        """Get the value of the Port.

        When connected, it recursively gets the source's value
        until a non connected port is found.
        """
        return self._value

    def set(self, value: PortType) -> None:
        """Set the value of the Port.

        Raises:
            SetConnectedPortError: when called and the port is connected.
        """
        if not isinstance(value, self._type):
            raise TypeError(
                f"Cannot set Port {self._name}[{self._type}] to a value "
                f"of {value}[{type(value)}]."
            )

        self._value = value

    def path(self) -> PurePosixPath:
        """The absolute path of this Port."""
        return self.component().path().with_suffix(f".{self.name()}")

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """The relative path of the port to the component."""
        if relative_to is self.component():
            path = PurePosixPath(f".{self.name()}")
        else:
            path = self.path().relative_to(relative_to.path())

        return path


PortLike = Union[Port[PortType], UUID]

__all__ = [
    "Port",
    "PortType",
    "PortLike",
]
