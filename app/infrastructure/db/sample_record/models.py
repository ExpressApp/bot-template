"""Database models declarations."""

from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.sqlalchemy import Base


class SampleRecordModel(Base):
    """Simple database model for example."""

    __tablename__ = "sample_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # noqa: WPS125
    record_data: Mapped[str]

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
