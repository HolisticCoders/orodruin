import cProfile
import os

import orodruin.commands
from orodruin.core import State


def to_profile(state: State) -> None:
    orodruin.commands.ImportNode(
        state, state.root_graph(), "RIG_IK", "orodruin-library"
    ).do()


if __name__ == "__main__":
    state = State()

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    cProfile.run("to_profile(state)", "tmp/import_node.prof")
