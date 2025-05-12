from fastapi import Path, Query, Request
from fastapi.responses import JSONResponse

from src.database.managers import UserManager
from src.api.api.base_api import BaseClassAPI
from src.common.logger import Logger


class UsersAPI(BaseClassAPI):
    def __init__(
            self,
            prefix: str,
            user_manager: UserManager

    ):
        super().__init__(prefix=prefix)

        self.user_manager = user_manager
        self.logger = Logger()

        @self.router.get("/")
        async def get_users(request: Request) -> JSONResponse:
            try:
                query_params = dict(request.query_params)
                self.logger.info(f"New GET {self.prefix}/?{"&".join([f"{key}={value}" for key, value in query_params.items()])}")
                users = await self.user_manager.get(**query_params)
                self.logger.info(f"Successfully retrieved {len(users)} users from database using query {query_params}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"got {len(users)} users", "data": [
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "password": user.password,
                        "created_at": user.created_at.timestamp()
                    } for user in users
                ]})

            except BaseException as e:
                self.logger.error(f"Error while processing request for getting users: {e.__class__.__name__}. {str(e)}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.post("/")
        async def create_user(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New POST {self.prefix}/ request received. Body: {payload}")
            try:
                email = payload.get("email")
                if not email:
                    self.logger.warning(f"bad request while processing request for user creation: incorrect format. Body: {payload}")
                    return JSONResponse(status_code=400, content={"status": "error", "message": "bad request, incorrect format"})

                existing_users = await self.user_manager.get(email=email)
                if existing_users:
                    self.logger.warning(f"bad request while processing request for user creation: user with email '{email}' already exists. Body: {payload}")
                    return JSONResponse(status_code=409, content={"status": "error", "message": f"bad request, user with email '{email}' already exists"})

                user = await self.user_manager.create(**payload)
                self.logger.info(f"User {user.id} crated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"User {user.id} created successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for user creation: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.patch("/")
        async def update_user(request: Request) -> JSONResponse:
            payload = await request.json()
            self.logger.info(f"New PATCH {self.prefix}/ request received. Body: {payload}")
            try:
                id = payload.get("id")
                if not id:
                    self.logger.warning(f"bad request while processing request for user update: incorrect format. Body: {payload}")
                    return JSONResponse(status_code=400, content={"status": "error", "message": "bad request, incorrect format"})

                existing_users = await self.user_manager.get(id=id)
                if not existing_users:
                    self.logger.warning(f"bad request while processing request for user update: user with id '{id}' not found. Body: {payload}")
                    return JSONResponse(status_code=404, content={"status": "error", "message": f"bad request, user with id '{id}' not found"})

                user = await self.user_manager.update(**payload)
                self.logger.info(f"User {user.id} updated successfully. Body: {payload}")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"User {user.id} updated successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for user update: {e.__class__.__name__}. {str(e)}. Body: {payload}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.delete("/{user_id}")
        async def delete_user(user_id: int = Path(...)) -> JSONResponse:
            self.logger.info(f"New DELETE {self.prefix}/{user_id} request received")
            try:
                users = await self.user_manager.get(id=user_id)
                if not users:
                    self.logger.warning(f"bad request while processing request for user deletion: User {user_id} not found")
                    return JSONResponse(status_code=404, content={"status": "success", "message": f"User {user_id} not found"})

                user = await self.user_manager.delete(id=user_id)
                self.logger.info(f"User {user_id} deleted successfully")
                return JSONResponse(status_code=200, content={"status": "success", "message": f"User {user_id} deleted successfully"})

            except BaseException as e:
                self.logger.error(f"Error while processing request for user deletion: {e.__class__.__name__}. {str(e)}. user_id={user_id}")
                return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

        @self.router.get("/test")
        async def test():
            return JSONResponse(status_code=200, content={"status": "success", "message": "Request received and processed successfully!"})
