# """Orodruin Library Management."""
# from __future__ import annotations

# import os
# from dataclasses import dataclass
# from pathlib import Path
# from typing import List, Optional

# from .component import Component
# from .serialization import ComponentDeserializer


# class NoRegisteredLibraryError(Exception):
#     """No libraries are registered."""


# class ComponentNotFoundError(Exception):
#     """Component not found in libraries."""


# class TargetDoesNotExistError(Exception):
#     """Target does not exist in library"""


# @dataclass
# class Library:
#     """Orodruin Library Class.

#     A Library is a collection of serialized Components.
#     Each subfolder of the collection represents a "target" implemention
#     of the components for the library.
#     The generic Components are saved in the "orodruin" target.
#     Any DCC Specific Component should be defined in the appropriate target folder.
#     """

#     path: Path

#     def name(self) -> str:
#         """Name of the Library."""
#         return self.path.name

#     def target_path(self, target_name: str) -> Optional[Path]:
#         """Return the full path of a target from its name."""
#         for target in self.path.iterdir():
#             if target.name == target_name:
#                 return target
#         return None

#     def targets(self) -> List[Path]:
#         """Return all the targets of this Library"""
#         return list(self.path.iterdir())

#     def get_component(self, component_name: str, target: str = "orodruin") -> Component:
#         """Return an Instantiated Component from a given name and target."""
#         target_path = self.target_path(target)

#         if not target_path:
#             raise TargetDoesNotExistError(f"Library {self.name} has no target {target}")

#         for component_path in target_path.iterdir():
#             if (
#                 component_path.suffix == ".json"
#                 and component_path.stem == component_name
#             ):
#                 component = ComponentDeserializer.component_from_json(
#                     component_path,
#                     component_type=component_name,
#                     library=self,
#                 )
#                 component.set_name(component_name)
#                 return component

#         raise ComponentNotFoundError(
#             f"No component named {component_name} found in any registered libraries"
#         )

#     def components(self, target: str = "orodruin") -> List[Component]:
#         """Return all the components of this library for the given target"""
#         target_path = self.target_path(target)

#         if not target_path:
#             raise TargetDoesNotExistError(f"Library {self.name} has no target {target}")

#         components: List[Component] = []
#         for component_path in target_path.iterdir():
#             if component_path.suffix == ".json":
#                 component = ComponentDeserializer.component_from_json(
#                     component_path,
#                     component_type=component_path.name,
#                     library=self,
#                 )
#                 component.set_name(component_path.name)

#                 components.append(component)

#         return components

#     def __eq__(self, o: object) -> bool:
#         if isinstance(o, str):
#             return os.fspath(self.path) == o

#         if isinstance(o, os.PathLike):
#             return self.path == o

#         if isinstance(o, Library):
#             return self.path == o.path

#         return False


# @dataclass
# class LibraryManager:
#     """Manager Class for multiple Libraries.

#     This class should not be instantiated and is simply an interface
#     over the "ORODRUIN_LIBRARIES" environment Variable.
#     """

#     libraries_env_var = "ORODRUIN_LIBRARIES"

#     @classmethod
#     def libraries(cls) -> List[Library]:
#         """List all the registered libraries."""
#         libraries_string = os.environ.get(cls.libraries_env_var)

#         if not libraries_string:
#             return []

#         return [Library(Path(p)) for p in libraries_string.split(";")]

#     @classmethod
#     def register_library(cls, path: Path) -> None:
#         """Register the given library."""

#         if not path.exists():
#             raise NotADirectoryError(f"path '{path}' does not exist.")

#         if not path.is_dir():
#             raise NotADirectoryError(f"path `{path}` is not a directory.")

#         libraries = cls.libraries()
#         library = Library(path)
#         if path not in libraries:
#             libraries.append(library)

#         cls._set_libraries_var(libraries)

#     @classmethod
#     def unregister_library(cls, path: Path) -> None:
#         """Unregister the given library."""
#         libraries = [l for l in cls.libraries() if l.path != path]

#         cls._set_libraries_var(libraries)

#     @classmethod
#     def _set_libraries_var(cls, libraries: List[Library]) -> None:
#         """Set the environment variable with the given libraries."""
#         libraries_string = ";".join([str(l.path) for l in libraries])
#         os.environ[cls.libraries_env_var] = libraries_string

#     @classmethod
#     def get_component(cls, component_name: str, target: str = "orodruin") -> Component:
#         """Get the component file from the libraries."""

#         namespace = None
#         if "::" in component_name:
#             namespace, component_name = component_name.split("::")

#         libraries = cls.libraries()
#         if not libraries:
#             raise NoRegisteredLibraryError("No libraries are registered")

#         if namespace:
#             for library in libraries:
#                 if namespace and namespace == library.name:
#                     try:
#                         return library.get_component(component_name, target)
#                     except (TargetDoesNotExistError, ComponentNotFoundError):
#                         pass
#         else:
#             for library in libraries:
#                 try:
#                     return library.get_component(component_name, target)
#                 except (TargetDoesNotExistError, ComponentNotFoundError):
#                     pass

#         raise ComponentNotFoundError(
#             f"No component named {component_name} found in any registered libraries"
#         )

#     @classmethod
#     def get_library(cls, name: str) -> Optional[Library]:
#         """Get a Library instance from a name."""
#         for library in cls.libraries():
#             if library.name() == name:
#                 return library

#         return None
