import logging
import sys
from loguru import logger
from typing import Optional
import os

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """Setup structured logger with Loguru"""
    
    # Get log level from environment or parameter
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with structured format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler for production
    if os.getenv("LOG_FILE"):
        logger.add(
            os.getenv("LOG_FILE"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="100 MB",
            retention="30 days",
            compression="gz"
        )
    
    # Create standard logger that forwards to loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Setup standard logging to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logging.getLogger(name)