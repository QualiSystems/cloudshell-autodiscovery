import unittest

import mock

from autodiscovery.common.utils import get_full_path
from autodiscovery.common.utils import get_logger


class TestUtils(unittest.TestCase):

    @mock.patch("autodiscovery.common.utils.logging")
    def test_get_logger(self, logging):
        """Check that method will return logger instance"""
        logger = mock.MagicMock()
        logging.getLogger.return_value = logger
        file_handler = mock.MagicMock()
        logging.FileHandler.return_value = file_handler
        # act
        result = get_logger()
        # verify
        self.assertEqual(result, logger)
        logging.getLogger.assert_called_once_with("autodiscovery")
        logging.FileHandler.assert_called_once_with("autodiscovery.log")
        logger.addHandler.assert_any_call(file_handler)

    @mock.patch("autodiscovery.common.utils.os")
    def test_get_full_path(self, os):
        """Check that function will use given arguments to create full path to the file"""
        dir1 = "test directory1"
        dir2 = "test directory2"
        filename = "test filename"
        base_dir = "base directory"
        joined_path = mock.MagicMock()
        os.path.split.return_value = [base_dir]
        os.path.join.return_value = joined_path
        # act
        result = get_full_path(dir1, dir2, filename)
        # verify
        self.assertEqual(result, joined_path)
        os.path.join.assert_called_once_with(base_dir, os.pardir, os.pardir, dir1, dir2, filename)
