"""All the types that can be assigned to a port.

to register a new type, it must be available in this module and
exported through the __all__ variable.

The ConnectPort command will try to cast the value of the source port
to the target's type.
All custom types should raise a TypeError if the provided value can't be casted
"""
from __future__ import annotations

from builtins import bool, float, int, str
from enum import Enum
from typing import List, Optional, TypeVar
from uuid import UUID

import attr


@attr.s
class Reference:
    """Reference to an orodruin node."""

    value: Optional[UUID] = attr.ib(default=None)


@attr.s(init=False)
class Vector2:
    """Vector2 representation class."""

    value: List[float]

    def __init__(self, value: Vector2 | List[float] | None = None) -> None:
        if value is None:
            self.value = [0.0, 0.0]

        if isinstance(value, Vector2):
            self.value = value.value

        if not isinstance(value, list) or len(value) != 9:
            raise TypeError(f"Invalid value {value} for {self.__class__.__name__}")


@attr.s(init=False)
class Vector3:
    """Vector3 representation class."""

    value: List[float]

    def __init__(self, value: Vector3 | List[float] | None = None) -> None:
        if value is None:
            self.value = [0.0, 0.0, 0.0]

        if isinstance(value, Vector3):
            self.value = value.value

        if not isinstance(value, list) or len(value) != 9:
            raise TypeError(f"Invalid value {value} for {self.__class__.__name__}")


@attr.s(init=False)
class Quaternion:
    """Quaternion representation class."""

    value: List[float]

    def __init__(self, value: Quaternion | List[float] | None = None) -> None:
        if value is None:
            self.value = [0.0, 0.0, 0.0, 1.0]

        if isinstance(value, Quaternion):
            self.value = value.value

        if not isinstance(value, list) or len(value) != 9:
            raise TypeError(f"Invalid value {value} for {self.__class__.__name__}")


@attr.s(init=False)
class Matrix3:
    """Matrix representation class."""

    value: List[float]

    def __init__(self, value: Matrix3 | List[float] | None = None) -> None:
        if value is None:
            # fmt: off
            self.value = [
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0,
            ]
            # fmt: on

        if isinstance(value, Matrix3):
            self.value = value.value

        if not isinstance(value, list) or len(value) != 9:
            raise TypeError(f"Invalid value {value} for {self.__class__.__name__}")


@attr.s(init=False)
class Matrix4:
    """Matrix representation class."""

    value: List[float]

    def __init__(self, value: Matrix4 | List[float] | None = None) -> None:
        if value is None:
            # fmt: off
            self.value = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ]
            # fmt: on

        if isinstance(value, Matrix4):
            self.value = value.value

        if not isinstance(value, list) or len(value) != 16:
            raise TypeError(f"Invalid value {value} for {self.__class__.__name__}")


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

    Reference = Reference
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
    "Reference",
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
