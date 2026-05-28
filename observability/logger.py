"""
Observability Structured Logger

Defines a custom structured logging setup that outputs highly readable,
color-coded console statements for local debugging, easily expandable to JSON formats.
"""

import sys
import logging
from typing import Any

# ANSI escape sequences for console coloring
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"

class ColoredFormatter(logging.Formatter):
    """Custom formatter to inject console colors depending on log levels and names."""
    def format(self, record: logging.LogRecord) -> str:
        level_name = record.levelname
        
        # Color codes based on severity
        if record.levelno == logging.DEBUG:
            color = CYAN
        elif record.levelno == logging.INFO:
            color = GREEN
        elif record.levelno == logging.WARNING:
            color = YELLOW
        elif record.levelno >= logging.ERROR:
            color = RED
        else:
            color = RESET
            
        # Highlight specific agent modules in blue/cyan
        module_name = record.name
        module_colored = f"{BLUE}{module_name}{RESET}"
        
        formatted_message = super().format(record)
        
        # Build final colored console string
        return (
            f"{color}[{level_name}]{RESET} "
            f"({module_colored}): "
            f"{formatted_message}"
        )


def setup_logger(name: str = "SQLAgent", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a colored structured logger instance.
    
    Args:
        name: Name of the logger category (e.g. 'SQLAgent.Graph').
        level: Logging level threshold.
        
    Returns:
        A ready-to-use logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers in case it gets initialized multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Format string
        formatter = ColoredFormatter(
            fmt="%(asctime)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    # Prevent propagation to root logger to ensure absolute control over double formatting
    logger.propagate = False
    
    return logger
