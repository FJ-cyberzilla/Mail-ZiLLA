# monitoring/logging_config.py
import logging

from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure structured JSON logging for production"""
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    log_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[log_handler])

