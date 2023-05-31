"""Database models declarations."""

from sqlalchemy.orm import Mapped, mapped_column

from app.db.sqlalchemy import Base


class RecordModel(Base):
    """Simple database model for example."""

    __tablename__ = "records"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )  # noqa: WPS125
    record_data: Mapped[str]

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
