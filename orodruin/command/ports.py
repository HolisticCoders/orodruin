from dataclasses import dataclass, field
from typing import Optional, Type
from uuid import UUID

from orodruin.port.port import Port, PortDirection

from ..component import Component
from ..graph import Graph
from .command import Command


@dataclass
class CreatePort(Command):

    _graph: Graph
    _component: Component
    _name: str
    _direction: PortDirection
    _type: Type

    _created_port: Port = field(init=False)

    def do(self) -> Port:
        port = Port(
            _name=self._name,
            _direction=self._direction,
            _type=self._type,
            _component=self._component,
        )

        self._graph.register_port(port)
        self._component.register_port(port)
        self._created_port = port
        return self._created_port

    def undo(self) -> None:
        # TODO: Delete all the connectionts from/to this Port
        self._graph.unregister_port(self._created_port.uuid())
        self._component.unregister_port(self._created_port.uuid())

    def redo(self) -> Port:
        # TODO: Recreate all the connections from/to this Port
        self._graph.register_port(self._created_port)
        self._component.register_port(self._created_port)
        return self._created_port


@dataclass
class DeletePort(Command):

    _graph: Graph
    _port_id: UUID

    _deleted_port: Port = field(init=False)
    _owner_component: Component = field(init=False)

    def do(self) -> None:
        # TODO: Delete all the connections from/to this component
        self._deleted_port = self._graph.unregister_port(self._port_id)
        self._owner_component = self._deleted_port.component()
        self._owner_component.unregister_port(self._port_id)

    def undo(self) -> Port:
        # TODO: Recreate all the connections from/to this component
        self._graph.register_port(self._deleted_port)
        self._owner_component.register_port(self._deleted_port)
        return self._deleted_port
