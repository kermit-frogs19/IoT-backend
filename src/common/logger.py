
# External imports
import logging

# Internal imports
from src.common.singleton import singleton


@singleton
class Logger:
    def __init__(self, level=logging.INFO):
        # Create a logger object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        # Check if the logger already has handlers, to avoid adding duplicate handlers
        if not self.logger.hasHandlers():
            # Create a console handler to log to the console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Create a logging format
            formatter = logging.Formatter('%(levelname)s:%(message)s')
            console_handler.setFormatter(formatter)

            # Add the console handler to the logger
            self.logger.addHandler(console_handler)

    def info(self, message, disable: bool = False):
        if not disable:
            self.logger.info(f"     {str(message)}")

    def error(self, message, disable: bool = False):
        if not disable:
            self.logger.error(f"    {str(message)}")

    def debug(self, message, disable: bool = False):
        if not disable:
            self.logger.debug(f"    {str(message)}")

    def warning(self, message, disable: bool = False):
        if not disable:
            self.logger.warning(f"  {str(message)}")

    def critical(self, message, disable: bool = False):
        if not disable:
            self.logger.critical(f" {str(message)}")
