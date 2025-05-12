from src.database.models.user import User
from src.database.database_client import DatabaseClient
from sqlalchemy import update, delete, select
from datetime import datetime


class UserManager:
    def __init__(
            self,
            db_client: DatabaseClient,
    ):
        self.db_client = db_client

    async def get(
            self,
            *,
            id: int = None,
            name: str = None,
            email: int = None,
            password: str = None,
            created_at: datetime = None
    ) -> list[User]:
        async with self.db_client.AsyncSessionDB() as session:
            stmt = select(User)

            if id is not None:
                stmt = stmt.where(User.id == id)
            if name is not None:
                stmt = stmt.where(User.name == name)
            if email is not None:
                stmt = stmt.where(User.email == email)
            if password is not None:
                stmt = stmt.where(User.password == password)
            if created_at is not None:
                stmt = stmt.where(User.created_at == created_at)

            result = await session.execute(stmt)
            return result.scalars().all()

    async def create(self, __user: User = None, name: str = None, email: str = None, password: str = None) -> User:
        async with self.db_client.AsyncSessionDB() as session:
            if not __user:
                if None in {name, email, password}:
                    raise ValueError(f"Incorrect values for user creation")
                user = User(name=name, email=email, password=password)
            else:
                user = __user

            session.add(user)
            await session.commit()
        return user

    async def update(self, __user: User = None, id: int = None, name: str = None, email: str = None, password: str = None) -> User:
        if not __user:
            if not id:
                raise ValueError(f"ID of user must be provided")
            values = {"name": name, "email": email, "password": password}
        else:
            values = {"name": __user.name, "email": __user.email, "password": __user.password}

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                update(User)
                .where(User.id == id if __user is None else User.id == __user.id)
                .values(
                    **{k: v for k, v in values.items() if v is not None}
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

            if not __user:
                result = await session.execute(
                    select(User).where(User.id == id)
                )
                return result.scalar_one_or_none()

            else:
                return __user

    async def delete(self, __user: User = None,  id: int = None) -> None:
        if not __user:
            if not id:
                raise ValueError(f"ID of user must be provided")
            condition = User.id == id
        else:
            condition = User.id == __user.id

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                delete(User)
                .where(condition)
            )
            await session.execute(stmt)
            await session.commit()

