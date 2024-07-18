import logging
from flask import abort

def error_wrapper(func):
    """
    A decorator function that wraps another function and handles any exceptions that occur during its execution.

    Args:
        func: The function to be wrapped.

    Returns:
        The wrapped function.

    Raises:
        Exception: If an exception occurs during the execution of the wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"Function {func.__name__} failed", exc_info=True)
            abort(400, description=f"Function {func.__name__} failed. Error: {str(e)}")
    
    return wrapper