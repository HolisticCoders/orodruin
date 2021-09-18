"""All the types that can be assigned to a port.

to register a new type, it must be available in this module and
exported through the __all__ variable.

All custom types should be dataclasses as serialization/deserialization
will assume any non built-in type is a dataclass.

Types will be instantiated in one of two ways when creating Ports:
1. If the class is a dataclass. the `new` class method will be called.
    It should _not_ take any argument and initialize all the
    fields to their default value.
2. Otherwise, simply instantiate the class.
"""
from __future__ import annotations

from builtins import bool, float, int, str
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Vector2:
    """Matrix representation class."""

    value: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))


@dataclass
class Vector3:
    """Matrix representation class."""

    value: Tuple[float, float, float] = field(default_factory=lambda: (0.0, 0.0, 0.0))


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
