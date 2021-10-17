"""All the types that can be assigned to a port.

to register a new type, it must be available in this module and
exported through the __all__ variable.

The ConnectPort command will try to cast the value of the source port
to the target's type.
All custom types should raise a TypeError if the provided value can't be casted
"""
from __future__ import annotations

from builtins import bool, float, int, str
import attr
from enum import Enum
from typing import List, TypeVar


@attr.s
class Vector2:
    """Vector2 representation class."""

    value: List[float] = attr.ib(factory=lambda: [0.0, 0.0])

    def __attrs_post_init__(self) -> None:
        if isinstance(self.value, Vector2):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, list) or len(self.value) != 2:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@attr.s
class Vector3:
    """Vector3 representation class."""

    value: List[float] = attr.ib(factory=lambda: [0.0, 0.0, 0.0])

    def __attrs_post_init__(self) -> None:
        if isinstance(self.value, Vector3):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, List) or len(self.value) != 3:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@attr.s
class Quaternion:
    """Quaternion representation class."""

    value: List[float] = attr.ib(factory=lambda: [0.0, 0.0, 0.0, 1.0])

    def __attrs_post_init__(self) -> None:
        if isinstance(self.value, Quaternion):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, list) or len(self.value) != 4:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@attr.s
class Matrix3:
    """Matrix representation class."""

    value: List[float] = attr.ib(
        # fmt: off
        factory=lambda: [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ]
        # fmt: on
    )

    def __attrs_post_init__(self) -> None:
        if isinstance(self.value, Matrix3):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, list) or len(self.value) != 9:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@attr.s
class Matrix4:
    """Matrix representation class."""

    value: List[float] = attr.ib(
        # fmt: off
        factory=lambda: [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ]
        # fmt: on
    )

    def __attrs_post_init__(self) -> None:
        if isinstance(self.value, Matrix4):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, list) or len(self.value) != 16:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


PortType = TypeVar(
    "PortType",
    Matrix3,
    Matrix4,
    Vector2,
    Vector3,
    Quaternion,
    bool,
    float,
    int,
    str,
)


class PortTypes(Enum):
    """Enum registering all the possible orodruin types."""

    Matrix3 = Matrix3
    Matrix4 = Matrix4
    Vector2 = Vector2
    Vector3 = Vector3
    Quaternion = Quaternion
    bool = bool
    float = float
    int = int
    str = str


__all__ = [
    "PortType",
    "PortTypes",
    "Matrix3",
    "Matrix4",
    "Vector2",
    "Vector3",
    "Quaternion",
    "bool",
    "float",
    "int",
    "str",
]
