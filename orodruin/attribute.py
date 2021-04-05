# pylint: disable = missing-class-docstring
"""All the possible Value Types a Port can have."""
from dataclasses import dataclass


@dataclass
class IntAttribute:
    default_value = 0


@dataclass
class FloatAttribute:
    default_value = 0.0


@dataclass
class BoolAttribute:
    default_value = True


@dataclass
class StringAttribute:
    default_value = ""


@dataclass
class MatrixAttribute:
    # fmt: off
    default_value = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    ]
    # fmt: on


@dataclass
class ComponentAttribute:
    default_value = None
