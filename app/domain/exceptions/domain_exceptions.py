"""Domain-specific exceptions."""


class DomainError(Exception):
    """Base exception for all domain-specific exceptions."""

    def __init__(self, message: str = "Domain error occurred"):
        self.message = message
        super().__init__(self.message)


class WrongRecordDataError(DomainError):
    """Raised when record data is not valid."""

    def __init__(self, message: str = "Wrong record data"):
        super().__init__(message)
