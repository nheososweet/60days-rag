"""
Utility functions for logging and debugging.
"""
import logging
import time
from functools import wraps
from typing import Callable


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger = get_logger(func.__module__)
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger = get_logger(func.__module__)
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
