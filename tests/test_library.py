# pylint: disable = missing-module-docstring, missing-function-docstring
from pathlib import Path

import pytest

from orodruin.component import Component
from orodruin.library import LibraryManager


@pytest.fixture(autouse=True)
def unregister_libraries():
    yield
    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library)


def test_register_library():
    assert len(LibraryManager.libraries()) == 0

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert len(LibraryManager.libraries()) == 1


def test_register_inexisting_library():

    library_path = Path("invalid path")
    with pytest.raises(NotADirectoryError):
        LibraryManager.register_library(library_path)


def test_register_file_as_library():

    library_path = Path(__file__)
    with pytest.raises(NotADirectoryError):
        LibraryManager.register_library(library_path)


def test_list_libraries():

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert library_path in LibraryManager.libraries()


def test_unregister_library():
    assert len(LibraryManager.libraries()) == 0

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert len(LibraryManager.libraries()) == 1

    LibraryManager.unregister_library(library_path)

    assert len(LibraryManager.libraries()) == 0


def test_get_component():
    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)
    component = LibraryManager.get_component("SimpleComponent")
    assert isinstance(component, Component)
