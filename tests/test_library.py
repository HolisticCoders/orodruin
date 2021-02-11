# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import Path

import pytest

from orodruin.library import (
    get_component,
    list_libraries,
    register_library,
    unregister_library,
)


@pytest.fixture(autouse=True)
def unregister_libraries():
    yield
    for library in list_libraries():
        unregister_library(library)


def test_register_library():
    assert len(list_libraries()) == 0

    library_path = (Path(__file__) / ".." / "library").resolve()
    register_library(library_path)

    assert len(list_libraries()) == 1


def test_register_inexisting_library():

    library_path = Path("invalid path")
    with pytest.raises(NotADirectoryError):
        register_library(library_path)


def test_register_file_as_library():

    library_path = Path(__file__)
    with pytest.raises(NotADirectoryError):
        register_library(library_path)


def test_list_libraries():

    library_path = (Path(__file__) / ".." / "library").resolve()
    register_library(library_path)

    assert library_path in list_libraries()


def test_remove_libraries():
    assert len(list_libraries()) == 0

    library_path = (Path(__file__) / ".." / "library").resolve()
    register_library(library_path)

    assert len(list_libraries()) == 1

    unregister_library(library_path)

    assert len(list_libraries()) == 0


def test_get_component():
    library_path = (Path(__file__) / ".." / "library").resolve()
    register_library(library_path)
    component = get_component("SimpleComponent")
    assert component == library_path / "orodruin" / "SimpleComponent.json"
