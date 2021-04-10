from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..component import Component  # pylint: disable = cyclic-import


@runtime_checkable
class Port(Protocol):
    """Protocol for all orodruin's Ports."""

    class Type(Enum):
        """Enum representing all the types an attribute can be."""

        int = 0
        float = 0.0
        bool = True
        string = ""
        reference: Optional["Component"] = None
        # fmt: off
        matrix = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]
        # fmt: on

    class Direction(Enum):
        """Directions a port can have."""

        input = "input"
        output = "output"

    @property
    def component(self) -> "Component":
        """The Component this Port is attached on."""
        return self._component

    @property
    def type(self) -> "Type":
        """Type of the port."""
        return self._type

    @property
    def direction(self) -> "Direction":
        """Direction of the port."""
        return self._direction

    @property
    def source(self) -> Optional["Port"]:
        """Returns the Port connected to the input of this Port"""

    @property
    def targets(self) -> List["Port"]:
        """Returns the Ports connected to the input of this Port"""

    def get(self) -> Any:
        """Return the value of the port."""

    def set(self, value: Any) -> None:
        """Return the value of the port."""

    def connect(self, other: "Port", force: bool = False) -> None:
        """Connect this port to another port."""

    def disconnect(self, other: "Port") -> None:
        """Disconnect this port from the other Port."""

    def external_connections(self) -> List[Tuple["Port", "Port"]]:
        """Returns all the connections external to the port's component."""

    def internal_connections(self) -> List[Tuple["Port", "Port"]]:
        """Returns all the connections internal to the port's component."""
