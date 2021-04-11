# pylint: disable = missing-module-docstring
# pylint: disable = missing-function-docstring
# pylint: disable = missing-class-docstring
from typing import Generator

import pytest

from orodruin.component import Component
from orodruin.graph_manager import GraphManager
from orodruin.port import PortDirection
from orodruin.port.types import Matrix


@pytest.fixture(autouse=True)
def clear_registered_components() -> Generator:

    yield
    GraphManager.clear_registered_components()


def test_arm_component() -> None:
    class ChainFK(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_multi_port("input", PortDirection.input, Matrix)
            self.add_multi_port("output", PortDirection.output, Matrix)
            self.sync_port_sizes(self.input, self.output)

    class ChainIK(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_port("base", PortDirection.input, Matrix)
            self.add_port("end", PortDirection.input, Matrix)
            self.add_multi_port(
                "output",
                PortDirection.output,
                Matrix,
                size=3,
            )

    class ChainBlender(Component):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_port("blender", PortDirection.input, float)
            self.add_multi_port("input_a", PortDirection.input, Matrix)
            self.add_multi_port("input_b", PortDirection.input, Matrix)
            self.add_multi_port("output", PortDirection.output, Matrix)

            self.sync_port_sizes(self.input_a, self.output)

    arm = Component.new("arm")
    arm.add_port("fk_ik_blend", PortDirection.input, float)
    arm.add_port("ik_base", PortDirection.input, Matrix)
    arm.add_port("ik_end", PortDirection.input, Matrix)
    arm.add_multi_port(
        "fk_matrices",
        PortDirection.input,
        Matrix,
        size=3,
    )
    arm.add_multi_port(
        "output",
        PortDirection.output,
        Matrix,
        size=3,
    )

    fk_chain = ChainFK.new("fk_chain")
    ik_chain = ChainIK.new("ik_chain")
    chain_blender = ChainBlender.new("chain_blender")
    fk_chain.parent = arm
    ik_chain.parent = arm
    chain_blender.parent = arm

    arm.ik_base.connect(ik_chain.base)
    arm.ik_end.connect(ik_chain.end)
    arm.fk_ik_blend.connect(chain_blender.blender)

    for i in range(3):
        arm.fk_matrices[i].connect(fk_chain.input)
        fk_chain.output[i].connect(chain_blender.input_a)
        ik_chain.output[i].connect(chain_blender.input_b)
        chain_blender.output[i].connect(arm.output[i])
