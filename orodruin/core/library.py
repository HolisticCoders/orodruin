"""Orodruin Library Management."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from orodruin.exceptions import NoRegisteredLibraryError, TargetDoesNotExistError


@dataclass
class Library:
    """Orodruin Library Class.

    A Library is a collection of serialized Nodes.
    Each subfolder of the collection represents a "target" implemention
    of the nodes for the library.
    The generic Nodes are saved in the "orodruin" target.
    Any DCC Specific Node should be defined in the appropriate target folder.
    """

    _path: Path

    def name(self) -> str:
        """Name of the Library."""
        return self._path.name

    def path(self) -> Path:
        """Path of the Library"""
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

    def nodes(self, target_name: str = "orodruin") -> List[Path]:
        """Return all the node paths for the given target."""
        target_path = self.target_path(target_name)

        if not target_path:
            raise TargetDoesNotExistError(
                f"Library {self.name} has no target {target_name}"
            )

        nodes = []
        for node_path in target_path.iterdir():
            if node_path.is_file():
                nodes.append(node_path)

        return nodes

    def find_node(
        self,
        node_name: str,
        target_name: str = "orodruin",
        extension: str = "json",
    ) -> Optional[Path]:
        """Return the path of a the given node for the given target name."""
        for node_path in self.nodes(target_name):
            if node_path.stem == node_name and node_path.suffix.endswith(extension):
                return node_path
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
        libraries = [l for l in cls.libraries() if l.path() != path]

        cls._set_libraries_var(libraries)

    @classmethod
    def _set_libraries_var(cls, libraries: List[Library]) -> None:
        """Set the environment variable with the given libraries."""
        libraries_string = ";".join([str(l.path()) for l in libraries])
        os.environ[cls.libraries_env_var] = libraries_string

    @classmethod
    def find_node(
        cls,
        node_name: str,
        library_name: Optional[str] = None,
        target_name: str = "orodruin",
        extension: str = "json",
    ) -> Optional[Path]:
        """Get the node file from the libraries."""

        libraries = cls.libraries()
        if not libraries:
            raise NoRegisteredLibraryError("No libraries are registered")

        if library_name:
            library = cls.find_library(library_name)
            if library:
                node_path = library.find_node(
                    node_name,
                    target_name,
                    extension,
                )
                if node_path:
                    return node_path
        else:
            for library in libraries:
                node_path = library.find_node(
                    node_name,
                    target_name,
                    extension,
                )
                if node_path:
                    return node_path

        return None

    @classmethod
    def find_library(cls, name: str) -> Optional[Library]:
        """Get a Library instance from a name."""
        for library in cls.libraries():
            if library.name() == name:
                return library

        return None
