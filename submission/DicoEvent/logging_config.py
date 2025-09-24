import sys
from loguru import logger

logger.remove()

logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}", level="INFO")

logger.add(
    "logs/application.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    rotation="1 day",
    level="INFO",
    enqueue=True,
)

logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    rotation="1 day",
    level="ERROR",
    enqueue=True,
)

app_logger = logger
