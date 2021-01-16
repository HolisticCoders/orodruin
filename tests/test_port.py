from uuid import uuid4

import pytest

from orodruin.port import Port, PortAlreadyConnected, PortNotConnected


def test_init_port():
    port = Port("port")
    assert port.name() == "port"


def test_init_component_with_uuid():
    uuid = uuid4()
    port = Port("port", uuid)
    assert port.uuid() == uuid


def test_set_port_name():
    port = Port("port")
    assert port.name() == "port"

    port.set_name("other name")
    assert port.name() == "other name"


def test_connect_ports():
    port_a = Port("port A")
    port_b = Port("port B")

    assert len(port_a.connections()) == 0
    assert len(port_b.connections()) == 0

    port_a.connect(port_b)

    assert len(port_a.connections()) == 1
    assert len(port_b.connections()) == 1

    assert port_a.connections()[0] is port_b
    assert port_b.connections()[0] is port_a


def test_connect_already_connected_ports():
    port_a = Port("port A")
    port_b = Port("port B")

    port_a.connect(port_b)
    with pytest.raises(PortAlreadyConnected):
        port_a.connect(port_b)


def test_disconnect_ports():
    port_a = Port("port A")
    port_b = Port("port B")

    port_a.connect(port_b)
    port_a.disconnect(port_b)


def test_disconnect_non_connected_ports():
    port_a = Port("port A")
    port_b = Port("port B")

    with pytest.raises(PortNotConnected):
        port_a.disconnect(port_b)
