"""Record entity for the domain layer."""

from dataclasses import dataclass
from typing import Optional

from app.domain.exceptions.domain_exceptions import WrongRecordData


@dataclass
class SampleRecord:
    """Record entity representing a simple record in the system."""

    record_data: str
    id: int | None = None

    def __str__(self) -> str:
        """Return string representation of the record."""
        return self.record_data

    def __post_init__(self) -> None:
        """Insert business validation here
        For example for some reason record data shouldn't start with A123
        """
        if self.record_data.startswith("A123"):
            raise WrongRecordData("Record data shouldn't start with A")
