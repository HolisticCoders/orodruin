import json
from uuid import uuid4, UUID

from orodruin.port import Port, PortSide


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class Component:
    def __init__(self, name, uuid=None) -> None:
        self._name = name

        if uuid:
            self._uuid = uuid
        else:
            self._uuid = uuid4()

        self._inputs = []
        self._outputs = []

        self._components = []
        self._parent = None

    def __getattr__(self, name: str):
        for port in self._inputs:
            if port.name() == name:
                return port

        for port in self._outputs:
            if port.name() == name:
                return port

    def build():
        pass

    def publish():
        pass

    def add_port(self, name, port_side):
        port = Port(name)

        if port_side == PortSide.input:
            self._inputs.append(port)
        elif port_side == PortSide.output:
            self._outputs.append(port)

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def uuid(self):
        return self._uuid

    def inputs(self):
        return self._inputs

    def outputs(self):
        return self._outputs

    def components(self):
        return self._components

    def _add_child(self, other):
        if other not in self._components:
            self._components.append(other)

    def parent(self):
        return self._parent

    def set_parent(self, other):
        self._parent = other
        other._add_child(self)

    def as_dict(self):
        data = {
            "name": self._name,
            "uuid": self._uuid,
            "components": [c.as_dict() for c in self._components],
        }

        inputs = []
        for port in self._inputs:
            inputs.append(port.as_dict())
        data["inputs"] = inputs

        outputs = []
        for port in self._outputs:
            outputs.append(port.as_dict())
        data["outputs"] = outputs

        return data

    def as_json(self, indent=2):
        return json.dumps(self.as_dict(), indent=indent, cls=UUIDEncoder)
