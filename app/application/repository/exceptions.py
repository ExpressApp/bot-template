class BaseRepositoryError(Exception):
    """Base exception for all repository-specific exceptions."""


class RecordDoesNotExistError(BaseRepositoryError):
    """Raised when an entity does not exist."""


class RecordUpdateError(BaseRepositoryError):
    """Raised when an update fails."""


class RecordDeleteError(BaseRepositoryError):
    """Raised when a delete fails."""


class RecordCreateError(BaseRepositoryError):
    """Raised when a creation fails."""


class RecordRetreiveError(BaseRepositoryError):
    """Raised when a get fails."""
