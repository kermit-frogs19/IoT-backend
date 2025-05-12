from fastapi import APIRouter
from typing import Callable, Optional, Any
from fastapi import Request
from fastapi.responses import JSONResponse

from src.common.logger import Logger

class BaseClassAPI:
    """
    This is an abstract class

    :param prefix: (str) literal that will be added to the beginning of every endpoint of the class
    :param tags: (str) key-word to group different endpoints in documentation
    :param default_code: (int) default code that will be returned be the server when the request is made to a
    non-existing endpoint
    :param default_msg: (str) default message that will be returned be the server when the request is made to a
    non-existing endpoint
    """

    def __init__(
            self,
            prefix: str,
            tags: str = None,
            default_code: int = None,
            default_msg: str = None
    ):
        self.prefix = prefix
        self.tags = tags
        self.default_code = default_code
        self.default_msg = default_msg

        self.router: APIRouter = self.create_router()
        self.logger = Logger()

    def create_router(self):

        # Process default values and parameters
        tags_par = [self.prefix.lstrip("/")]
        code_par = 404
        msg_par = "Not found"

        if self.tags is not None:
            tags_par = [self.tags]
        if self.default_code is not None:
            code_par = self.default_code
        if self.default_msg is not None:
            msg_par = self.default_msg

        return APIRouter(
            prefix=self.prefix,
            tags=tags_par,
            responses={code_par: {"description": msg_par}},
        )