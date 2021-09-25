import pytest

from orodruin.core import State


@pytest.fixture(name="state")
def fixture_state() -> State:
    """Create and return a root graph."""
    return State()
