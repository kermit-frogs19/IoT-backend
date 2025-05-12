from src.database.models._base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, DateTime,ForeignKey, JSON


class Device(Base):
    __tablename__ = "devices"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    user_id = mapped_column(Integer, ForeignKey("users.id"), index=True)
    last_seen = mapped_column(DateTime(timezone=True))
    status = mapped_column(String)
    regime = mapped_column(JSON)


