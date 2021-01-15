from enum import Enum
from uuid import uuid4


class PortError(Exception):
    pass


class PortAlreadyConnected(PortError):
    pass


class PortNotConnected(PortError):
    pass


class PortSide(Enum):
    input = 1
    output = 2


class Port:
    def __init__(self, name, uuid=None) -> None:
        self._name = name
        self._connections = []

        # TODO: implement port types
        # self._value: Any = None

        if uuid:
            self._uuid = uuid
        else:
            self._uuid = uuid4()

    def connect(self, other):
        if other in self._connections:
            raise PortAlreadyConnected(
                f"port {self.name()} is already connected to {other.name()}"
            )
        self._connections.append(other)
        other._connections.append(self)

    def disconnect(self, other):
        if other not in self._connections:
            raise PortNotConnected(
                f"port {self.name()} is not connected to {other.name()}"
            )
        self._connections.remove(other)
        other._connections.remove(self)

    def connections(self):
        return self._connections

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def uuid(self):
        return self._uuid

    def as_dict(self):
        data = {
            "name": self._name,
            "uuid": self._uuid,
            "connections": [c.uuid() for c in self._connections],
        }

        return data
