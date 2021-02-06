# pylint: disable = missing-module-docstring
# pylint: disable = missing-function-docstring
# pylint: disable = missing-class-docstring
import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager
from orodruin.port import PortType


@pytest.fixture(autouse=True)
def clear_registered_components():

    yield
    GraphManager.clear_registered_components()


def test_arm_component():
    class ChainFK(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_port_collection("input", PortType.matrix)
            self.add_port_collection("output", PortType.matrix)
            self.sync_port_sizes(self.input, self.output)

    class ChainIK(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_port("base", PortType.matrix)
            self.add_port("end", PortType.matrix)
            self.add_port_collection("output", PortType.matrix, size=3)

    class ChainBlender(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_port("blender", PortType.float)
            self.add_port_collection("input_a", PortType.matrix)
            self.add_port_collection("input_b", PortType.matrix)
            self.add_port_collection("output", PortType.matrix)

            self.sync_port_sizes(self.input_a, self.output)

    arm = Component("arm")
    arm.add_port("fk_ik_blend", PortType.float)
    arm.add_port("ik_base", PortType.matrix)
    arm.add_port("ik_end", PortType.matrix)
    arm.add_port_collection("fk_matrices", PortType.matrix, size=3)
    arm.add_port_collection("output", PortType.matrix, size=3)

    fk_chain = ChainFK("fk_chain")
    ik_chain = ChainIK("ik_chain")
    chain_blender = ChainBlender("chain_blender")

    arm.ik_base.connect(ik_chain.base)
    arm.ik_end.connect(ik_chain.end)
    arm.fk_ik_blend.connect(chain_blender.blender)

    for i in range(3):
        arm.fk_matrices[i].connect(fk_chain.input)
        fk_chain.output[i].connect(chain_blender.input_a)
        ik_chain.output[i].connect(chain_blender.input_b)
        chain_blender.output[i].connect(arm.output[i])
