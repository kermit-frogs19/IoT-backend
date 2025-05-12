from src.database.models._base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime, UTC


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    email = mapped_column(String, unique=True)
    password = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))