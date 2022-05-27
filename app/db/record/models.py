"""Database models declarations."""

from sqlalchemy import Column, Integer, String

from app.db.sqlalchemy import Base


class RecordModel(Base):
    """Simple database model for example."""

    __tablename__ = "records"

    id: int = Column(Integer, primary_key=True, autoincrement=True)  # noqa: WPS125
    record_data: str = Column(String)

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
