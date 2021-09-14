# """Orodruin Library Management."""
# from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# from .component import Component
# from .serialization import ComponentDeserializer


class NoRegisteredLibraryError(Exception):
    """No libraries are registered."""


class ComponentNotFoundError(Exception):
    """Component not found in libraries."""


class TargetDoesNotExistError(Exception):
    """Target does not exist in library"""


class LibraryDoesNotExistError(Exception):
    """Library does not found in the registered libraries"""


@dataclass
class Library:
    """Orodruin Library Class.

    A Library is a collection of serialized Components.
    Each subfolder of the collection represents a "target" implemention
    of the components for the library.
    The generic Components are saved in the "orodruin" target.
    Any DCC Specific Component should be defined in the appropriate target folder.
    """

    _path: Path

    def name(self) -> str:
        """Name of the Library."""
        return self._path.name

    def path(self) -> Path:
        return self._path

    def target_path(self, target_name: str) -> Optional[Path]:
        """Return the full path of a target from its name."""
        for target in self._path.iterdir():
            if target.name == target_name:
                return target
        return None

    def targets(self) -> List[Path]:
        """Return all the targets of this Library"""
        return list(self._path.iterdir())

    def find_component(
        self,
        component_name: str,
        target_name: str = "orodruin",
    ) -> Optional[Path]:
        target_path = self.target_path(target_name)

        if not target_path:
            raise TargetDoesNotExistError(
                f"Library {self.name} has no target {target_name}"
            )

        for component_path in target_path.iterdir():
            if (
                component_path.suffix == ".json"
                and component_path.stem == component_name
            ):
                return component_path

        return None


class LibraryManager:
    """Manager Class for multiple Libraries.

    This class should not be instantiated and is simply an interface
    over the "ORODRUIN_LIBRARIES" environment Variable.
    """

    libraries_env_var = "ORODRUIN_LIBRARIES"

    def __init__(self) -> None:
        raise NotImplementedError(
            f"Type {self.__class__.__name__} cannot be instantiated."
        )

    @classmethod
    def libraries(cls) -> List[Library]:
        """List all the registered libraries."""
        libraries_string = os.environ.get(cls.libraries_env_var)

        if not libraries_string:
            return []

        return [Library(Path(p)) for p in libraries_string.split(";")]

    @classmethod
    def register_library(cls, path: Path) -> None:
        """Register the given library."""

        if not path.exists():
            raise NotADirectoryError(f"path '{path}' does not exist.")

        if not path.is_dir():
            raise NotADirectoryError(f"path `{path}` is not a directory.")

        libraries = cls.libraries()
        library = Library(path)
        if path not in libraries:
            libraries.append(library)

        cls._set_libraries_var(libraries)

    @classmethod
    def unregister_library(cls, path: Path) -> None:
        """Unregister the given library."""
        libraries = [l for l in cls.libraries() if l._path != path]

        cls._set_libraries_var(libraries)

    @classmethod
    def _set_libraries_var(cls, libraries: List[Library]) -> None:
        """Set the environment variable with the given libraries."""
        libraries_string = ";".join([str(l._path) for l in libraries])
        os.environ[cls.libraries_env_var] = libraries_string

    @classmethod
    def find_component(
        cls,
        component_name: str,
        library_name: Optional[str] = None,
        target_name: str = "orodruin",
    ) -> Optional[Path]:
        """Get the component file from the libraries."""

        libraries = cls.libraries()
        if not libraries:
            raise NoRegisteredLibraryError("No libraries are registered")

        if library_name:
            library = cls.find_library(library_name)
            if library:
                component = library.find_component(component_name, target_name)
                if component:
                    return component
        else:
            for library in libraries:
                component = library.find_component(component_name, target_name)
                if component:
                    return component

        return None

    @classmethod
    def find_library(cls, name: str) -> Optional[Library]:
        """Get a Library instance from a name."""
        for library in cls.libraries():
            if library.name() == name:
                return library

        return None
