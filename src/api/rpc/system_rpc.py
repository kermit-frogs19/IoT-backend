from sqlalchemy import update, delete, select

from src.database.managers import *
from src.database.models import *
from src.database.database_client import DatabaseClient
from src.common.logger import Logger
from src.logic.time_checker import TimeChecker


class SystemRPC:
    def __init__(
            self,
            db_client: DatabaseClient,
            device_manager: DeviceManager,
            command_manager: CommandManager,
            time_checker: TimeChecker
    ):
        self.db_client = db_client
        self.device_manager = device_manager
        self.command_manager = command_manager
        self.time_checker = time_checker

        self.logger = Logger()

    async def get_commands(self, device_id: int) -> list:
        await self.time_checker.check(device_id)
        commands = await self.command_manager.get(device_id=device_id, status=0)
        commands_dict = [{
            "id": command.id,
            "date_time": command.date_time.timestamp(),
            "device_id": command.device_id,
            "command": command.command,
            "kwargs": command.kwargs,
            "status": command.status
        } for command in commands]

        async with self.db_client.AsyncSessionDB() as session:
            stmt = (
                update(Command)
                .where(Command.id.in_({command.id for command in commands}))
                .values(**{"status": 1})
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

        self.logger.info(f"Successfully retrieved {len(commands)} commands for device {device_id}")
        return commands_dict

    async def command_completed(self, command_id: int, status: int) -> None:
        commands = await self.command_manager.get(id=command_id)
        if not commands:
            raise ValueError(f"No commands found with command_id={command_id}")

        command = commands[0]
        command.status = status
        await self.command_manager.update(command)
        self.logger.info(f"Command {command.id} - {command.command}({command.kwargs}) completed with status {status}")
        return None

    async def new_event(self, device_id: int, event: dict) -> None:
        self.logger.info(f"New event received from device {device_id}. event: {event}")

    async def test(self, message: str) -> str:
        return f"Message '{message}' received successfully!"

