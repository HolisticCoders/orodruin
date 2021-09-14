# pylint: disable = missing-module-docstring, missing-function-docstring
from os import PathLike
from pathlib import Path
from typing import Generator

import pytest

from orodruin.library import LibraryManager


@pytest.fixture(autouse=True)
def unregister_libraries() -> Generator:
    yield
    for library in LibraryManager.libraries():
        LibraryManager.unregister_library(library.path())


def test_register_library() -> None:
    assert len(LibraryManager.libraries()) == 0

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert len(LibraryManager.libraries()) == 1


def test_register_inexisting_library() -> None:

    library_path = Path("invalid path")
    with pytest.raises(NotADirectoryError):
        LibraryManager.register_library(library_path)


def test_register_file_as_library() -> None:

    library_path = Path(__file__)
    with pytest.raises(NotADirectoryError):
        LibraryManager.register_library(library_path)


def test_list_libraries() -> None:

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert library_path in [l.path() for l in LibraryManager.libraries()]


def test_unregister_library() -> None:
    assert len(LibraryManager.libraries()) == 0

    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    assert len(LibraryManager.libraries()) == 1

    LibraryManager.unregister_library(library_path)

    assert len(LibraryManager.libraries()) == 0


def test_get_component() -> None:
    library_path = (Path(__file__) / ".." / "TestLibrary").resolve()
    LibraryManager.register_library(library_path)

    component = LibraryManager.find_component("SimpleComponent")

    assert isinstance(component, PathLike)
