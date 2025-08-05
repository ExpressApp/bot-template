"""Record entity for the domain layer."""

from dataclasses import dataclass



@dataclass
class SampleRecord:
    """Record entity representing a simple record in the system."""

    record_data: str
    name: str
    id: int | None = None

    def __str__(self) -> str:
        """Return string representation of the record."""
        return f"id={self.id}, record_data={self.record_data}, name={self.name}"
