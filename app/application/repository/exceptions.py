from app.decorators.mapper.factories import ContextAwareError


class BaseRepositoryError(ContextAwareError):
    """Base exception for all repository-specific exceptions."""


class RecordDoesNotExistError(BaseRepositoryError):
    """Raised when an entity does not exist."""


class RecordUpdateError(BaseRepositoryError):
    """Raised when an update fails."""


class RecordDeleteError(BaseRepositoryError):
    """Raised when a delete fails."""


class RecordCreateError(BaseRepositoryError):
    """Raised when a creation fails."""


class RecordRetrieveError(BaseRepositoryError):
    """Raised when a get fails."""


class RecordAlreadyExistsError(BaseRepositoryError):
    """Raised when a record already exists."""


class ForeignKeyError(BaseRepositoryError):
    """Raised when a foreign key constraint is violated."""


class ValidationError(BaseRepositoryError):
    """Raised when a validation error occurs."""
