"""All the types that can be assigned to a port.

to register a new type, it must be available in this module and
exported through the __all__ variable.

The ConnectPort command will try to cast the value of the source port
to the target's type.
All custom types should raise a TypeError if the provided value can't be casted
"""
from __future__ import annotations

from builtins import bool, float, int, str
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Vector2:
    """Matrix representation class."""

    value: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))

    def __post_init__(self) -> None:
        if isinstance(self.value, Vector2):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, tuple) or len(self.value) != 2:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@dataclass
class Vector3:
    """Matrix representation class."""

    value: Tuple[float, float, float] = field(default_factory=lambda: (0.0, 0.0, 0.0))

    def __post_init__(self) -> None:
        if isinstance(self.value, Vector3):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, tuple) or len(self.value) != 3:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@dataclass
class Matrix3:
    """Matrix representation class."""

    # fmt: off
    value: Tuple[
        float, float, float,
        float, float, float,
        float, float, float,
    ] = field(
        default_factory=lambda: (
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        )
    )
    # fmt: on

    def __post_init__(self) -> None:
        if isinstance(self.value, Matrix3):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, tuple) or len(self.value) != 9:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


@dataclass
class Matrix4:
    """Matrix representation class."""

    # fmt: off
    value: Tuple[
        float, float, float, float,
        float, float, float, float,
        float, float, float, float,
        float, float, float, float,
    ] = field(
        default_factory=lambda: (
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
    )
    # fmt: on

    def __post_init__(self) -> None:
        if isinstance(self.value, Matrix4):
            self.value = self.value.value  # pylint: disable = no-member

        if not isinstance(self.value, tuple) or len(self.value) != 16:
            raise TypeError(f"Invalid value {self.value} for {self.__class__.__name__}")


__all__ = [
    "Matrix3",
    "Matrix4",
    "Vector2",
    "Vector3",
    "bool",
    "float",
    "int",
    "str",
]
