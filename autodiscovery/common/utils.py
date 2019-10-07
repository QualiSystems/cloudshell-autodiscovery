import logging
import os


def get_logger(file_path=None):
    """Get logger.

    :param file_path:
    :rtype: logging.Logger
    """
    if file_path is None:
        file_path = "autodiscovery.log"

    logger = logging.getLogger("autodiscovery")
    handler = logging.FileHandler(file_path)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


def get_full_path(*args):
    """Get full path to the file.

    :param args:
    :return:
    """
    dir_name = os.path.split(os.path.abspath(__file__))[0]
    return os.path.join(dir_name, os.pardir, os.pardir, *args)
