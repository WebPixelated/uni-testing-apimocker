import sys
from loguru import logger
from core.config import settings


def setup_logger() -> None:
    """Configure loguru: remove default sink, add console + rotating file."""
    logger.remove()

    # Console sink
    logger.add(
        sys.stdout,
        level=settings.log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
    )

    # File sink (rotating)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        format=("{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}"),
    )


# Initialize on startup
setup_logger()

__all__ = ["logger"]
