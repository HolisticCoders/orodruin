class NoRegisteredLibraryError(Exception):
    """No libraries are registered."""


class TargetDoesNotExistError(Exception):
    """Target does not exist in library"""


class LibraryDoesNotExistError(Exception):
    """Library does not found in the registered libraries"""


class ComponentNotFoundError(Exception):
    """Component not found in libraries."""


class ComponentError(Exception):
    """Generic Component Error"""


class ParentToSelfError(ComponentError):
    """Component parented to itself."""


class ComponentDoesNotExistError(ComponentError):
    """Component does not exist."""


class PortDoesNotExistError(ValueError):
    """Given component doesn't exist."""


class PortAlreadyConnectedError(ConnectionError):
    """Port Already Connected Error."""


class ConnectionOnSameComponentError(ConnectionError):
    """Both ports about to be connected are on the same component."""


class OutOfScopeConnectionError(ConnectionError):
    """Connection from two components not in the same scope."""


class ConnectionToSameDirectionError(ConnectionError):
    """Two ports of the same direction and scope are being connected together."""


class ConnectionToDifferentDirectionError(ConnectionError):
    """Two ports of the component and its parent direction are being connected together
    while they have the same direction.
    """
