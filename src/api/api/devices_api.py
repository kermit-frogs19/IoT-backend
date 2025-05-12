from fastapi import Path, Query, Request
from fastapi.responses import JSONResponse

from src.database.managers import DeviceManager
from src.api.api.base_api import BaseClassAPI
from src.common.logger import Logger


class DevicesAPI(BaseClassAPI):
    def __init__(
            self,
            prefix: str,
            device_manager: DeviceManager
    ):
        super().__init__(prefix=prefix)

        self.device_manager = device_manager
        self.logger = Logger()

        @self.router.get("/")
        async def get_devices(request: Request) -> JSONResponse:
            try:
                query_params = dict(request.query_params)
                self.logger.info(f"New GET {self.prefix}/?{"&".join([f"{key}={value}" for key, value in query_params.items()])} request received")
                devices = await self.device_manager.get(**query_params)
                self.logger.info(f"Successfully retrieved {len(devices)} devices devices from database using query {query_params}")
                return JSONResponse(status_code=200,
                                    content={"status": "success", "message": f"got {len(devices)} devices", "data": [
                                        {
                                            "id": device.id,
                                            "name": device.name,
                                            "user_id": device.user_id,
                                            "last_seen": device.last_seen.timestamp(),
                                            "status": device.status,
                                            "regime": device.regime
                                        } for device in devices
                                    ]})

            except BaseException as e:
                self.logger.error(f"Error while processing request for getting devices: {e.__class__.__name__}. {str(e)}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.post("/")
        async def create_device(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New POST {self.prefix}/ request received. Body: {payload}")
            try:
                name = payload.get("name")
                user_id = payload.get("user_id")

                if None in {name, user_id}:
                    self.logger.warning(f"bad request while processing request for device creation: incorrect format. Body: {payload}")
                    return JSONResponse(status_code=400, content={"status": "error", "message": "bad request, incorrect format"})

                existing_devices = await self.device_manager.get(name=name, user_id=user_id)
                if existing_devices:
                    self.logger.warning(f"bad request while processing request for device creation: device with name '{name}' already exists. Body: {payload}")
                    return JSONResponse(status_code=409, content={"status": "error", "message": f"bad request, device with name '{name}' already exists"})

                device = await self.device_manager.create(**payload)
                self.logger.info(f"Device {device.id} crated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Device {device.id} created successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for device creation: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.patch("/")
        async def update_device(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New PATCH {self.prefix}/ request received. Body: {payload}")
            try:
                id = payload.get("id")
                if not id:
                    self.logger.warning(f"bad request while processing request for device update: incorrect format. Body: {payload}")
                    return JSONResponse(status_code=400, content={"status": "error", "message": "bad request, incorrect format"})

                existing_device = await self.device_manager.get(id=id)
                if not existing_device:
                    self.logger.warning(f"bad request while processing request for device update: device with id '{id}' not found. Body: {payload}")
                    return JSONResponse(status_code=404, content={"status": "error", "message": f"bad request, device with id '{id}' not found"})

                device = await self.device_manager.update(**payload)
                self.logger.info(f"Device {device.id} updated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Device {device.id} updated successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for device update: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.delete("/{device_id}")
        async def delete_device(device_id: int = Path(...)) -> JSONResponse:
            self.logger.info(f"New DELETE {self.prefix}/{device_id} request received")
            try:
                devices = await self.device_manager.get(id=device_id)
                if not devices:
                    self.logger.warning(f"bad request while processing request for device deletion: Device {device_id} not found")
                    return JSONResponse(status_code=404, content={"status": "success", "message": f"Device {device_id} not found"})

                device = await self.device_manager.delete(id=device_id)
                self.logger.info(f"Device {device_id} deleted successfully")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"Device {device_id} deleted successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for device deletion: {e.__class__.__name__}. {str(e)}. device_id={device_id}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})
