# pylint: disable = missing-module-docstring, missing-function-docstring, pointless-statement
from typing import Callable

import pytest

from orodruin.component import Component
from orodruin.port import PortType
from orodruin.port_collection import PortCollection


def test_init_port(create_component: Callable[..., Component]):
    component = create_component("component")
    port = PortCollection("port", PortType.int, component)
    assert port.name() == "port"


def test_create_port_collection(create_component: Callable[..., Component]):
    component = create_component("component")

    assert len(component.ports()) == 0

    component.add_port_collection("my_port_collection", PortType.int)

    assert isinstance(component.my_port_collection, PortCollection)

    assert len(component.ports()) == 1


def test_access_sub_port(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port_collection("my_multi_port", PortType.int, size=1)

    component.my_multi_port[0]


def test_access_nonexisting_sub_port(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port_collection("my_multi_port", PortType.int)

    with pytest.raises(IndexError):
        component.my_multi_port[0]


def test_sync_ports(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port_collection("input", PortType.int)
    component.add_port_collection("output", PortType.int)

    component.sync_port_sizes(component.input, component.output)

    component.input.add_port()

    assert len(component.output.ports()) == 1
