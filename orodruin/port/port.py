from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Generic, Type, TypeVar
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import


class PortDirection(Enum):
    """Directions a port can have."""

    input = "input"
    output = "output"


T = TypeVar("T")  # pylint: disable = invalid-name


@dataclass
class Port(Generic[T]):
    """Orodruin's Port class

    A Port is only meant to be attached on a Component
    It can be connected to other Ports and hold a value
    """

    _name: str
    _direction: PortDirection
    _type: Type[T]
    _component: Component

    _value: T = field(init=False)

    _uuid: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self._value = self._type()

    def component(self) -> Component:
        """The Component this Port is attached on."""
        return self._component

    def type(self) -> Type[T]:
        """Type of the port."""
        return self._type

    def direction(self) -> PortDirection:
        """Direction of the port."""
        return self._direction

    def uuid(self) -> UUID:
        """UUID of this port."""
        return self._uuid

    def get(self) -> T:
        """Get the value of the Port.

        When connected, it recursively gets the source's value
        until a non connected port is found.
        """
        return self._value

    def set(self, value: T) -> None:
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

    def name(self) -> str:
        """Name of the port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the port."""
        self._name = name

    def path(self) -> PurePosixPath:
        """The Path of this Port, absolute or relative."""
        if not self._component:
            return PurePosixPath(self.name())
        path = self._component.path().with_suffix(f".{self.name()}")
        return path

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Port relative to Component."""
        if relative_to is self._component:
            path = PurePosixPath(f".{self.name()}")
        else:
            path = self.path().relative_to(relative_to.path())

        return path
