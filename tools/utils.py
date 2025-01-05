from logging import Logger, config, getLogger
from .constants import LOGGING_CONFIG

__all__ = ["get_logger"]

def get_logger(name: str) -> Logger:
    config.dictConfig(LOGGING_CONFIG)
    return getLogger(name)
