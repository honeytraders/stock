import structlog
import sys
from honeytrade.config import config

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if config.DEBUG else structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(config.LOG_LEVEL),
        cache_logger_on_first_use=True,
    )

    # Root logger
    logger = structlog.get_logger()
    logger.info("📡 Logging system initialized", level=config.LOG_LEVEL)
    return logger