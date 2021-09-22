import pytest

from orodruin.core import Scene


@pytest.fixture(name="scene")
def fixture_scene() -> Scene:
    """Create and return a root graph."""
    return Scene()
