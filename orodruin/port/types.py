# pylint: disable = too-few-public-methods
from builtins import bool, float, int, str


class Matrix:
    """Matrix representation class."""

    def __init__(self) -> None:
        # fmt: off
        self.value = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]
        # fmt: on


__all__ = [
    "int",
    "str",
    "float",
    "bool",
    "Matrix",
]
