from fastapi import Path, Query, Request
from fastapi.responses import JSONResponse

from src.database.managers import CommandManager
from src.api.api.base_api import BaseClassAPI
from src.common.logger import Logger


class CommandsAPI(BaseClassAPI):
    def __init__(
            self,
            prefix: str,
            command_manager: CommandManager
    ):
        super().__init__(prefix=prefix)

        self.command_manager = command_manager
        self.logger = Logger()

        @self.router.get("/")
        async def get_commands(request: Request) -> JSONResponse:
            try:
                query_params = dict(request.query_params)
                self.logger.info(f"New GET {self.prefix}/?{"&".join([f"{key}={value}" for key, value in query_params.items()])} request received")
                commands = await self.command_manager.get(**query_params)
                self.logger.info(f"Successfully retrieved {len(commands)} commands from database using query {query_params}")
                return JSONResponse(status_code=200,
                                    content={"status": "success", "message": f"got {len(commands)} commands", "data": [
                                        {
                                            "id": command.id,
                                            "date_time": command.date_time.timestamp(),
                                            "device_id": command.device_id,
                                            "command": command.command,
                                            "kwargs": command.kwargs,
                                            "status": command.status
                                        } for command in commands
                                    ]})

            except BaseException as e:
                self.logger.error(f"Error while processing request for getting commands: {e.__class__.__name__}. {str(e)}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.post("/")
        async def create_device(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New POST {self.prefix}/ request received. Body: {payload}")
            try:
                command = await self.command_manager.create(**payload)
                self.logger.info(f"Command {command.id} crated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Command {command.id} created successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for command creation: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.patch("/")
        async def update_device(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New PATCH {self.prefix}/ request received. Body: {payload}")
            try:
                id = payload.get("id")
                if not id:
                    self.logger.warning(f"bad request while processing request for command update: incorrect format. Body: {payload}")
                    return JSONResponse(status_code=400, content={"status": "error", "message": "bad request, incorrect format"})

                existing_commands = await self.command_manager.get(id=id)
                if not existing_commands:
                    self.logger.warning(f"bad request while processing request for command update: command with id '{id}' not found. Body: {payload}")
                    return JSONResponse(status_code=404, content={"status": "error", "message": f"bad request, command with id '{id}' not found"})

                command = await self.command_manager.update(**payload)
                self.logger.info(f"Command {command.id} updated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Command {command.id} updated successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for command update: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.delete("/{command_id}")
        async def delete_device(command_id: int = Path(...)) -> JSONResponse:
            self.logger.info(f"New DELETE {self.prefix}/{command_id} request received")
            try:
                commands = await self.command_manager.get(id=command_id)
                if not commands:
                    self.logger.warning(f"bad request while processing request for device deletion: Command {command_id} not found")
                    return JSONResponse(status_code=404, content={"status": "success", "message": f"bad request, command {command_id} not found"})

                device = await self.command_manager.delete(id=command_id)
                self.logger.info(f"Device {command_id} deleted successfully")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Command {command_id} deleted successfully"})

            except BaseException as e:
                self.logger.error(
                    f"Error while processing request for device deletion: {e.__class__.__name__}. {str(e)}. command_id={command_id}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})
