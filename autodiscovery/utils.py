import logging


def get_logger(file_path=None):
    """

    :param file_path:
    :return:
    """
    if file_path is None:
        file_path = "autodiscovery.log"

    logger = logging.getLogger('autodiscovery')
    handler = logging.FileHandler(file_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
