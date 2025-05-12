from src.database.managers import DeviceManager, CommandManager
from src.database.models import Command
from src.common.logger import Logger
from datetime import datetime, UTC


class TimeChecker:
    def __init__(
            self,
            device_manager: DeviceManager,
            command_manager: CommandManager
    ):
        self.device_manager = device_manager
        self.command_manager = command_manager
        self.logger = Logger()

    async def check(self, device_id: int) -> None:
        devices = await self.device_manager.get(id=device_id)
        if not devices:
            raise Exception(f"No device found with id: {device_id}")

        device = devices[0]
        now_utc = datetime.now(UTC)
        hour_minute_now = now_utc.strftime("%H:%M")
        state = device.regime.get(hour_minute_now)
        if state is None:
            return

        command = await self.command_manager.create(Command(
            date_time=now_utc,
            device_id=device.id,
            command="turn_on",
            kwargs={},
            status=0
        ))
        return None


