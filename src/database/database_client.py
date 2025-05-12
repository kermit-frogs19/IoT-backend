import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.database.models import *


class DatabaseClient:
    def __init__(
            self,
            db_dsn: str
    ):
        self.db_dsn = db_dsn

        self._engine = create_async_engine(self.db_dsn, echo=True)
        self.AsyncSessionDB = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def start(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


