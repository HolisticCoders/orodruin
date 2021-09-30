class NoRegisteredLibraryError(Exception):
    """No libraries are registered."""


class TargetDoesNotExistError(Exception):
    """Target does not exist in library"""


class LibraryDoesNotExistError(Exception):
    """Library does not found in the registered libraries"""


class NodeNotFoundError(Exception):
    """Node not found in libraries."""


class NodeError(Exception):
    """Generic Node Error"""


class ParentToSelfError(NodeError):
    """Node parented to itself."""


class NodeDoesNotExistError(NodeError):
    """Node does not exist."""


class PortDoesNotExistError(ValueError):
    """Given node doesn't exist."""


class PortAlreadyConnectedError(ConnectionError):
    """Port Already Connected Error."""


class ConnectionOnSameNodeError(ConnectionError):
    """Both ports about to be connected are on the same node."""


class OutOfScopeConnectionError(ConnectionError):
    """Connection from two nodes not in the same scope."""


class ConnectionToSameDirectionError(ConnectionError):
    """Two ports of the same direction and scope are being connected together."""


class ConnectionToDifferentDirectionError(ConnectionError):
    """Two ports of the node and its parent direction are being connected together
    while they have the same direction.
    """
