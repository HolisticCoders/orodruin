from typing import Callable, Type

import pytest

from orodruin.core import Component, Port, PortDirection


@pytest.fixture(name="root")
def fixture_root() -> Component:
    """Create and return a root component."""
    return Component("root")


@pytest.fixture(name="create_port")
def fixture_create_port() -> Callable[..., Port]:
    """Return a function to create a port."""

    def _create_port(
        component: Component,
        name: str,
        direction: PortDirection = PortDirection.input,
        _type: Type = int,
    ) -> Port:
        _port = Port(name, direction, _type, component)
        component.register_port(_port)
        return _port

    return _create_port


@pytest.fixture(name="port")
def fixture_port(create_port: Callable[..., Port]) -> Port:
    """Create a component with a port."""
    component = Component("my_component")
    return create_port(component, "my_port")
