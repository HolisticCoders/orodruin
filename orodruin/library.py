"""Orodruin Library Management."""
import os
from pathlib import Path
from typing import List

LIBRARIES_ENV_VAR = "ORODRUIN_LIBRARIES"


class NoRegisteredLibraryError(Exception):
    """No libraries are registered."""


class ComponentNotFoundError(Exception):
    """Component not found in libraries."""


def list_libraries() -> List[os.PathLike]:
    """List all the registered libraries."""
    libraries_string = os.environ.get(LIBRARIES_ENV_VAR)

    if libraries_string:
        return [Path(p) for p in libraries_string.split(";")]

    return []


def register_library(path: os.PathLike) -> None:
    """Register the given library."""

    if not path.exists():
        raise NotADirectoryError(f"path '{path}' does not exist.")

    if not path.is_dir():
        raise NotADirectoryError(f"path `{path}` is not a directory.")

    libraries = list_libraries()
    if path not in libraries:
        libraries.append(os.fspath(path))

    _set_libraries_var(libraries)


def unregister_library(path: os.PathLike) -> None:
    """Unregister the given library."""
    libraries = list_libraries()

    if path in libraries:
        libraries.remove(path)

    _set_libraries_var(libraries)


def _set_libraries_var(libraries: List[os.PathLike]) -> None:
    """Set the environment variable with the given libraries."""
    libraries = [os.fspath(p) for p in libraries]
    libraries_string = ";".join(libraries)
    os.environ[LIBRARIES_ENV_VAR] = libraries_string


def get_component(component_name: str) -> os.PathLike:
    """Get the component file from the libraries.

    This is a very naïve implementation that returns the first matching file.
    """
    if "::" in component_name:
        namespace, component_name = component_name.split("::")
    else:
        namespace = None

    libraries = list_libraries()
    if not libraries:
        raise NoRegisteredLibraryError("No libraries are registered")

    for library in libraries:
        if namespace and namespace == library:
            library_path = library
            break
    else:
        library_path = libraries[0]

    orodruin_folder = library_path / "orodruin"
    for item in orodruin_folder.iterdir():
        if item.is_file():
            if item.stem == component_name:
                return item

    raise ComponentNotFoundError(
        f"No component named {component_name} found in any registered libraries"
    )
