import logging
from dotenv import load_dotenv
from os import getenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "information": logging.INFO,
    "warn": logging.WARN,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_log_level(log_level: str):
    log_level = log_level.lower()
    return LOG_LEVELS.get(log_level, logging.INFO)


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: blue + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(
    class_name: str, level=get_log_level(getenv("SERVICE_LOG_LEVEL"))
) -> logging.Logger:

    new_logger = logging.getLogger(class_name)
    if len(new_logger.handlers) > 0:
        return new_logger

    file_handler = logging.handlers.TimedRotatingFileHandler(
        f"logs/{class_name}.log", when="H", interval=12, backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    new_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    new_logger.addHandler(stream_handler)
    new_logger.setLevel(level)
    new_logger.propagate = False

    return new_logger
