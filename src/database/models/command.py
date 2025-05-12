from src.database.models._base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
from datetime import datetime, UTC, timezone


class Command(Base):
    __tablename__ = "commands"

    id = mapped_column(Integer, primary_key=True)
    date_time = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    device_id = mapped_column(Integer, ForeignKey("devices.id"), index=True)
    command = mapped_column(String)
    kwargs = mapped_column(JSON)
    status = mapped_column(Integer)
