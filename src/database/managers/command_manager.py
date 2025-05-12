from src.database.models import Device, Command
from src.database.database_client import DatabaseClient
from sqlalchemy import update, delete, select
from datetime import datetime


class CommandManager:
    def __init__(
            self,
            db_client: DatabaseClient,
    ):
        self.db_client = db_client

    async def get(
            self,
            *,
            id: int = None,
            date_time: datetime = None,
            device_id: int = None,
            command: str = None,
            kwargs: dict = None,
            status: int = None
    ) -> list[Command]:
        async with self.db_client.AsyncSessionDB() as session:
            stmt = select(Command)

            if id is not None:
                stmt = stmt.where(Command.id == id)
            if date_time is not None:
                stmt = stmt.where(Command.date_time == date_time)
            if device_id is not None:
                stmt = stmt.where(Command.device_id == device_id)
            if command is not None:
                stmt = stmt.where(Command.command == command)
            if kwargs is not None:
                stmt = stmt.where(Command.kwargs == kwargs)
            if status is not None:
                stmt = stmt.where(Command.status == status)

            result = await session.execute(stmt)
            return result.scalars().all()

    async def create(
            self,
            __command: Command = None,
            date_time: datetime = None,
            device_id: int = None,
            command: str = None,
            kwargs: dict = None,
            status: int = None,
    ) -> Command:
        async with self.db_client.AsyncSessionDB() as session:
            if not __command and any(value is None for value in [date_time, device_id, command, kwargs, status]):
                raise ValueError(f"Incorrect values for user creation")

            # Step 1: Find the user by email
            result = await session.execute(
                select(Device).where(Device.id == device_id if not __command else Device.id == __command.device_id)
            )
            device = result.scalar_one_or_none()
            if not device:
                raise ValueError(f"No device found with id: {device_id}")

            # Step 2: Create the device with user_id
            if not __command:
                command_ = Command(
                    date_time=date_time,
                    device_id=device.id,
                    command=command,
                    kwargs=kwargs,
                    status=status,
                )
            else:
                command_ = __command

            session.add(command_)
            await session.commit()
        return command_

    async def update(
            self,
            __command: Command = None,
            id: int = None,
            date_time: datetime = None,
            device_id: int = None,
            command: str = None,
            kwargs: dict = None,
            status: int = None
    ) -> Command:
        if not __command:
            if not id:
                raise ValueError(f"ID of user must be provided")
            values = {"date_time": date_time, "device_id": device_id, "command": command, "kwargs": kwargs, "status": status}
        else:
            values = {"date_time": __command.date_time, "device_id": __command.device_id, "command": __command.command, "kwargs": __command.kwargs, "status": __command.status}

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                update(Command)
                .where(Command.id == id if __command is None else Command.id == __command.id)
                .values(
                    **{k: v for k, v in values.items() if v is not None}
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

            if not __command:
                result = await session.execute(
                    select(Command).where(Command.id == id)
                )
                return result.scalar_one_or_none()

            else:
                return __command

    async def delete(self, __command: Command = None, id: int = None) -> None:
        if not __command:
            if not id:
                raise ValueError(f"ID of device must be provided")
            condition = Command.id == id
        else:
            condition = Command.id == __command.id

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                delete(Command)
                .where(condition)
            )
            await session.execute(stmt)
            await session.commit()

