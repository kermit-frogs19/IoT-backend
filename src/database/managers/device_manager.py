from src.database.models import Device, User
from src.database.database_client import DatabaseClient
from sqlalchemy import update, delete, select
from datetime import datetime, UTC


class DeviceManager:
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
            user_id: int = None,
            status: str = None
    ) -> list[Device]:
        async with self.db_client.AsyncSessionDB() as session:
            stmt = select(Device)

            if id is not None:
                stmt = stmt.where(Device.id == id)
            if name is not None:
                stmt = stmt.where(Device.name == name)
            if user_id is not None:
                stmt = stmt.where(Device.user_id == user_id)
            if status is not None:
                stmt = stmt.where(Device.status == status)

            result = await session.execute(stmt)
            return result.scalars().all()

    async def create(
            self,
            __device: Device = None,
            name: str = None,
            user_id: int = None,
            status: str = None,
            regime: dict = None
    ) -> Device:
        async with self.db_client.AsyncSessionDB() as session:
            if not __device and any(val is None for val in [name, user_id, status, regime]):
                raise ValueError(f"Incorrect values for device creation")

            # Step 1: Find the user by email
            result = await session.execute(
                select(User).where(User.id == user_id if __device is None else User.id == __device.user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"No user found with id: {user_id}")

            # Step 2: Create the device with user_id
            if not __device:
                device = Device(
                    name=name,
                    user_id=user.id,
                    last_seen=datetime.now(UTC),
                    status=status,
                    regime=regime
                )
            else:
                device = __device

            session.add(device)
            await session.commit()
        return device

    async def update(
            self,
            __device: Device = None,
            id: int = None,
            name: str = None,
            user_id: int = None,
            last_seen: datetime = None,
            status: str = None,
            regime: dict = None
    ) -> Device:
        if not __device:
            if not id:
                raise ValueError(f"ID of user must be provided")
            values = {"name": name, "user_id": user_id, "last_seen": last_seen, "status": status, "regime": regime}
        else:
            values = {"name": __device.name, "user_id": __device.user_id, "last_seen": __device.last_seen, "status": __device.status, "regime": __device.regime}

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                update(Device)
                .where(Device.id == id if __device is None else Device.id == __device.id)
                .values(
                    **{k: v for k, v in values.items() if v is not None}
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

            if not __device:
                result = await session.execute(
                    select(Device).where(Device.id == id)
                )
                return result.scalar_one_or_none()

            else:
                return __device

    async def delete(self, __device: Device = None, id: int = None) -> None:
        if not __device:
            if not id:
                raise ValueError(f"ID of device must be provided")
            condition = Device.id == id
        else:
            condition = Device.id == __device.id

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                delete(Device)
                .where(condition)
            )
            await session.execute(stmt)
            await session.commit()

