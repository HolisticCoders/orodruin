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
from typing import List


@dataclass
class Matrix:
    """Matrix representation class."""

    value: List[float] = field(
        default_factory=lambda: [
            # fmt: off
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
            # fmt: on
        ]
    )


__all__ = [
    "int",
    "str",
    "float",
    "bool",
    "Matrix",
]
