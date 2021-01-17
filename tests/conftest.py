# pylint: disable = missing-module-docstring, redefined-outer-name
from typing import Callable, Iterator, Optional
from uuid import UUID

from pytest import fixture

from orodruin.component import Component


@fixture
def create_component() -> Iterator[Callable[[str, Optional[UUID]], Component]]:
    """Create Component.

    The created components will be deleted after the test.
    """
    created_components = []

    def _create_component(name: str, uuid: Optional[UUID] = None):
        component = Component(name, uuid)
        created_components.append(component)
        return component

    yield _create_component

    for component in created_components:
        component.delete()


@fixture
def root_component(create_component: Callable[..., Component]) -> Iterator[Component]:
    """Create root Component."""
    yield create_component("root")
