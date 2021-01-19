# pylint: disable = missing-module-docstring, missing-function-docstring, pointless-statement
from typing import Callable

import pytest

from orodruin.component import Component
from orodruin.multiport import MultiPort
from orodruin.port import PortType


def test_init_port(create_component: Callable[..., Component]):
    component = create_component("component")
    port = MultiPort("port", PortType.int, component)
    assert port.name() == "port"


def test_create_multiport(create_component: Callable[..., Component]):
    component = create_component("component")

    assert len(component.ports()) == 0

    component.add_port("my_multi_port", PortType.int, multi=True)

    assert isinstance(component.my_multi_port, MultiPort)

    assert len(component.ports()) == 1


def test_access_sub_port(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port("my_multi_port", PortType.int, multi=True)

    component.my_multi_port.add_port()
    component.my_multi_port[0]


def test_access_nonexisting_sub_port(create_component: Callable[..., Component]):
    component = create_component("component")
    component.add_port("my_multi_port", PortType.int, multi=True)

    with pytest.raises(IndexError):
        component.my_multi_port[0]
