import logging
from flask import abort

def error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"Function {func.__name__} failed", exc_info=True)
            abort(400, description=f"Function {func.__name__} failed. Error: {str(e)}")
    
    return wrapper