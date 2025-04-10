import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "app.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 2
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = int(os.environ.get("LOG_LEVEL", "20"))  # 20 = INFO


class TopInsertRotatingFileHandler(RotatingFileHandler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            if self.shouldRollover(record):
                self.doRollover()

            if not os.path.exists(self.baseFilename):
                open(self.baseFilename, "a").close()

            with open(self.baseFilename, "r+") as f:
                content = f.read()
                f.seek(0, 0)
                f.write(f"{self.format(record)}\n{content}")
        except Exception:
            self.handleError(record)


class LogColorerFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        logging.Formatter.__init__(self, fmt, datefmt, style)  # type: ignore

    def format(self, record):
        # Still apply the default formatter
        uncolored = logging.Formatter.format(self, record)

        reset = "\x1b[0m"

        color = "\x1b[36m"  # Cyan (default, for DEBUG level)
        if record.levelno >= logging.CRITICAL:
            color = "\x1b[41m\x1b[37m"  # Red bg, white text
        elif record.levelno >= logging.ERROR:
            color = "\x1b[31m"  # Red text
        elif record.levelno >= logging.WARNING:
            color = "\x1b[33m"  # Yellow text
        elif record.levelno >= logging.INFO:
            color = "\x1b[37m"  # White text

        # If the logged string is already colored in places, allow that to override this
        colored = color + uncolored.replace(reset, reset + color) + reset
        return colored


class LoggerSingleton:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls.setup_logger()
        return cls._instance

    @staticmethod
    def setup_logger() -> logging.Logger:
        logger = logging.getLogger("application_logger")
        logger.setLevel(LOG_LEVEL)

        handlers = [
            TopInsertRotatingFileHandler(
                LOG_FILE, mode="a", maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8", delay=False
            ),
            logging.StreamHandler(),
        ]

        for handler in handlers:
            handler.setFormatter(logging.Formatter(LOG_FORMAT))
            # Colorize the console output
            if handler.__class__.__name__ == "StreamHandler":
                handler.setFormatter(LogColorerFormatter(LOG_FORMAT))
            handler.setLevel(LOG_LEVEL)
            logger.addHandler(handler)

        return logger


logger = LoggerSingleton.get_logger()