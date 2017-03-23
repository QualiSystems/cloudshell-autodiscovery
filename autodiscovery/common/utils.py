import logging
import os
import sys


def get_logger(file_path=None):
    """

    :param file_path:
    :return:
    """
    if file_path is None:
        file_path = "autodiscovery.log"

    # full log messages
    logger = logging.getLogger('autodiscovery')
    handler = logging.FileHandler(file_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # console messages
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger


def get_full_path(*args):
    """

    :param args:
    :return:
    """
    dir_name = os.path.split(os.path.abspath(__file__))[0]
    return os.path.join(dir_name, os.pardir, os.pardir, *args)
