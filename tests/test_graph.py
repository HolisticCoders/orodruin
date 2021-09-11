# def test_connect_ports() -> None:
#     component_a = Component("component_a")
#     component_b = Component("component_b")
#     port_a = Port("port_a", PortDirection.output, int, component_a)
#     port_b = Port("port_b", PortDirection.input, int, component_b)
#     component_a.register_port(port_a)
#     component_b.register_port(port_b)

#     assert len(component_a.port_a.targets()) == 0
#     assert component_b.port_b.source() is None

#     component_a.port_a.connect(component_b.port_b)

#     assert len(component_a.port_a.targets()) == 1

#     assert component_a.port_a.targets()[0] is component_b.port_b
#     assert component_b.port_b.source() is component_a.port_a


# def test_connect_already_connected_ports() -> None:
#     component_a = Component("component_a")
#     component_b = Component("component_b")
#     component_a.register_port("port_a", PortDirection.output, int)
#     component_b.register_port("port_b", PortDirection.input, int)

#     component_a.port_a.connect(component_b.port_b)
#     with pytest.raises(PortAlreadyConnectedError):
#         component_a.port_a.connect(component_b.port_b)


# def test_disconnect_ports() -> None:
#     component_a = Component("component_a")
#     component_b = Component("component_b")
#     component_a.register_port("port_a", PortDirection.output, int)
#     component_b.register_port("port_b", PortDirection.input, int)

#     component_a.port_a.connect(component_b.port_b)
#     component_a.port_a.disconnect(component_b.port_b)


# def test_connect_different_type_ports() -> None:
#     component_a = Component("component_a")
#     component_b = Component("component_b")
#     component_a.register_port("output", PortDirection.output, bool)
#     component_b.register_port("input", PortDirection.input, int)

#     with pytest.raises(TypeError):
#         component_a.output.connect(component_b.input)


# def test_get_connected_port_value(create_port: Callable[..., Port]) -> None:
#     component_a = Component("component")
#     port_a = create_port(component_a, "output", PortDirection.output, int)

#     component_b = Component("component")
#     component_b.register_port("input", PortDirection.input, int)

#     component_a.output.connect(component_b.input)

#     component_a.output.set(42)

#     assert component_b.input.get() == 42


# def test_parent_to_self() -> None:
#     component = Component("component")

#     with pytest.raises(ParentToSelfError):
#         component.set_parent_graph(component.graph())


# def test_parent_component() -> None:
#     parent = Component("parent")
#     child = Component("child")

#     child.set_parent_graph(parent.graph())

#     assert child.parent_component() is parent
#     assert child in parent.graph().components().values()
