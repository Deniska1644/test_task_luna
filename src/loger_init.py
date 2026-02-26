"""Единая настройка логера: один вызов настраивает корневой логер, все модули используют logging.getLogger(__name__)."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import settings


def setup_logger() -> logging.Logger:
    """
    Настраивает корневой логер (консоль + ротируемый файл).
    Вызвать один раз при старте приложения (например, в lifespan).
    В любом модуле использовать: logger = logging.getLogger(__name__).
    """
    root = logging.getLogger()
    if root.handlers:
        return root
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    level = getattr(logging, settings.LOGGER_LVL.upper(), logging.INFO)
    root.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        filename=logs_dir / "project.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    return root
