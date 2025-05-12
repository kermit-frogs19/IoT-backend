from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


