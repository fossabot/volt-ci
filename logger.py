"""
Logger

This is a wrapper that handles logs in the system
"""
import os
import sys
from loguru import logger


# configurations for log handling

# info log configurations
logger.add(
    sink=sys.stdout,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="INFO"
)

# error logs
logger.add(
    sink=sys.stderr,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="ERROR"
)

# debug logs
logger.add(
    sink=sys.stdout,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="DEBUG"
)

# warning logs
logger.add(
    sink=sys.stdout,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="WARNING"
)

# critical logs
logger.add(
    sink=sys.stderr,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="CRITICAL"
)

# trace logs
logger.add(
    sink=sys.stderr,
    backtrace=True
    if os.environ.get("ENV", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="TRACE"
)