# pylint: disable = missing-class-docstring
"""All the possible Value Types a Port can have."""
from dataclasses import dataclass


@dataclass
class IntAttribute:
    python_type = int
    default_value = 0


@dataclass
class FloatAttribute:
    python_type = float
    default_value = 0.0


@dataclass
class BoolAttribute:
    python_type = bool
    default_value = True


@dataclass
class StringAttribute:
    python_type = str
    default_value = ""


@dataclass
class MatrixAttribute:
    python_type = None
    # fmt: off
    default_value = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    ]
    # fmt: on
