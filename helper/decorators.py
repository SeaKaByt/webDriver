# decorators.py
import functools
import logging
from datetime import datetime

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def debug_out_line(func):
    """
    Decorator that logs function entry/exit with arguments and execution time
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get class instance if method
        self = args[0] if len(args) > 0 and hasattr(args[0], '__class__') else None

        # Log function entry
        func_name = f"{self.__class__.__name__}.{func.__name__}" if self else func.__name__
        logger.debug(f"Entering {func_name} with args: {args[1:]} kwargs: {kwargs}")

        # Record start time
        start_time = datetime.now()

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Calculate execution time
            duration = (datetime.now() - start_time).total_seconds()

            # Log successful exit
            logger.debug(f"Exiting {func_name} - Duration: {duration:.3f}s - Result: {result}")
            return result

        except Exception as e:
            # Log any errors
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error in {func_name} - Duration: {duration:.3f}s - Exception: {str(e)}")
            raise

    return wrapper