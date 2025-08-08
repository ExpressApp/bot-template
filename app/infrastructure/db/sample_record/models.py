"""Database models declarations."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.sqlalchemy import Base


class SampleRecordModel(Base):
    """Simple database model for example."""

    __tablename__ = "sample_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_data: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("length(record_data) >= 1", name="record_data_min_length"),
        CheckConstraint("length(name) >= 1", name="name_min_length"),
    )

    def __repr__(self) -> str:
        """Show string representation of a record."""
        return f"{self.name}:{self.record_data}"
