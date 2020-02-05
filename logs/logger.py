import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler

def get_my_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler('logs/logging.log', when='d', interval=14, backupCount=5)
    fh.setLevel(logging.WARNING)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
