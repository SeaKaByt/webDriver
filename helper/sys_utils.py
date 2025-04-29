from helper.logger import logger

def raise_with_log(message, exc_type=Exception):
    logger.error(message)
    raise exc_type(message)
