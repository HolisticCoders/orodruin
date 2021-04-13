from __future__ import annotations

from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple, Type, TypeVar

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import
    from .single_port import SinglePort  # pylint: disable = cyclic-import

T = TypeVar("T")  # pylint: disable = invalid-name


class PortDirection(Enum):
    """Directions a port can have."""

    input = "input"
    output = "output"


@runtime_checkable
class Port(Protocol[T]):
    """Protocol for all orodruin's Ports."""

    def component(self) -> Component:
        """The Component this Port is attached on."""

    def type(self) -> Type[T]:
        """Type of the port."""

    def direction(self) -> PortDirection:
        """Direction of the port."""

    def source(self) -> Optional[SinglePort[T]]:
        """Returns the Port connected to the input of this Port"""

    def targets(self) -> List[SinglePort[T]]:
        """Returns the Ports connected to the input of this Port"""

    def get(self) -> T:
        """Return the value of the port."""

    def set(self, value: T) -> None:
        """Return the value of the port."""

    def connect(self, other: Port[T], force: bool = False) -> None:
        """Connect this port to another port."""

    def disconnect(self, other: Port[T]) -> None:
        """Disconnect this port from the other Port."""

    def external_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections external to the port's component."""

    def internal_connections(self) -> Sequence[Tuple[Port[T], Port[T]]]:
        """Returns all the connections internal to the port's component."""

    def name(self) -> str:
        """Name of the port."""

    def set_name(self, name: str) -> None:
        """Set the name of the port."""

    def path(self) -> PurePosixPath:
        """Absolute Path of object."""

    def relative_path(self, relative_to: Component) -> PurePosixPath:
        """Path of the Object to relative another one."""
