import asyncio
import logging
from uvicorn import Config, Server
from fastapi.middleware.cors import CORSMiddleware
from ezRPC import Receiver
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import grpc
from concurrent import futures
import time
import ping_pb2
import ping_pb2_grpc

from src.common.logger import Logger

# Load environment variables from .env file & create a logger instance before making any internal imports
load_dotenv()
logger = Logger()

from src.database.database_client import DatabaseClient
from src.database.models import *
from src.database.managers import *
from src.logic.time_checker import TimeChecker
from src.api.api.users_api import UsersAPI
from src.api.api.devices_api import DevicesAPI
from src.api.api.commands_api import CommandsAPI
from src.api.rpc.system_rpc import SystemRPC

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.DEBUG,
)

class PingerServicer(ping_pb2_grpc.PingerServicer):
    def Ping(self, request, context):
        return ping_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ping_pb2_grpc.add_PingerServicer_to_server(PingerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()


# Replace with your actual credentials
DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/postgres"


# Class initialization
database_client = DatabaseClient(db_dsn=DATABASE_URL)
user_manager = UserManager(db_client=database_client)
device_manager = DeviceManager(db_client=database_client)
command_manager = CommandManager(db_client=database_client)
time_checker = TimeChecker(device_manager=device_manager, command_manager=command_manager)

# Initializing API classes
users_api = UsersAPI("/users", user_manager=user_manager)
devices_api = DevicesAPI("/devices", device_manager=device_manager)
commands_api = CommandsAPI("/commands", command_manager=command_manager)

# Initializing RPC classes
system_rpc = SystemRPC(db_client=database_client, device_manager=device_manager, command_manager=command_manager, time_checker=time_checker)


# If the app is running in production (i.e. in Unix-based system) - try to use uvloop event loop, instead of asyncio.
# Because uvloop is not supported  on Windows
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("system: Using uvloop for asyncio event loop")
except ImportError:
    uvloop = None
    logger.warning("system: Failed to import/connect uvloop for asyncio event loop")


# Configure the actions the app will take before startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Actions before server starts
    try:
        logger.info(f"system: Server Started")
        await system_start()

    except Exception as e:
        logger.error(f"system: Error starting schedulers {e.__class__.__name__} {str(e)}")

    yield

    # Actions when server stops
    await system_stop()
    logger.info("system: System stopped - Application shutdown")

# Initializing and configuring RPC and REST servers
fastapi_app = FastAPI(
    title="IoT-backend",
    lifespan=lifespan
)
ezrpc_server = Receiver(
    title="IoT-backend-RPC",
    host="0.0.0.0",
    port=8000,
    enable_tls=False,
    enable_ipv6=True,
    custom_cert_file_loc="/app/cert.pem",
    custom_cert_key_file_loc="/app/key.pem"
)

# Connecting routes of API classes to the FastAPI server
fastapi_app.include_router(router=users_api.router)
fastapi_app.include_router(router=devices_api.router)
fastapi_app.include_router(router=commands_api.router)


# Adding CORS middleware to FastAPI app
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def dummy() -> None:
    return None


# Connecting methods of SystemRPC class to ezRPC server
ezrpc_server.add_class_instance(instance=system_rpc)
ezrpc_server.add_function(dummy)

# Initializing uvicorn server and connecting the FastAPI instance to it
uvicorn_server = Server(Config(app=fastapi_app, host="0.0.0.0", port=443))


@ezrpc_server.function(description="Get sum of 2 integers")
async def get_sum(a: int, b: int) -> int:
    return a + b


@ezrpc_server.function(description="Get subtraction of 2 integers")
async def get_subtraction(a: int, b: int) -> int:
    return a - b


@ezrpc_server.function(description="Echo...")
async def echo(phrase: str) -> str:
    return phrase


async def system_start():
    await database_client.start()


async def system_stop():
    # Stop both ezRPC and REST servers on exit
    ezrpc_server.shutdown()


async def main():
    config = Config(app=fastapi_app, host="0.0.0.0", port=5000)
    server = Server(config)

    # Run both REST and RPC (ezRPC) servers in the same app and host, but on different ports
    try:
        await asyncio.gather(
            server.serve(),
            ezrpc_server.run()
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.error("system: System stopped manually")


if __name__ == "__main__":
    serve()
    # asyncio.run(main())
    # asyncio.run(rpc.run())






