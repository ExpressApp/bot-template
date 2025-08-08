from app.decorators.mapper.factories import ContextAwareError


class MessageValidationError(ContextAwareError):
    """Base class for message validation errors."""
