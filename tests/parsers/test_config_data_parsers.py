import unittest

import mock

from autodiscovery.parsers.config_data_parsers import (
    AutoDiscoveryException,
    JSONConfigDataParser,
    get_config_data_parser,
)


class TestConfigDataParsers(unittest.TestCase):
    def test_get_config_data_parser(self):
        """Check that method will return JSONConfigDataParser instance."""
        # act
        result = get_config_data_parser(file_name="test_file.json")
        # verify
        self.assertIsInstance(result, JSONConfigDataParser)

    def test_get_config_data_parser_invalid_file_format(self):
        """Method should raise exception if provided file is in invalid format."""
        with self.assertRaisesRegexp(
            AutoDiscoveryException, "Invalid Additional Config Data file format"
        ):
            get_config_data_parser(file_name="test_file.invalid")


class TestJSONConfigDataParser(unittest.TestCase):
    def setUp(self):
        self.config_file = mock.MagicMock()
        self.json_config_parser = JSONConfigDataParser()

    @mock.patch("autodiscovery.parsers.config_data_parsers.open")
    @mock.patch("autodiscovery.parsers.config_data_parsers.json")
    def test_parse(self, json_lib, open_):
        expected_res = mock.MagicMock()
        json_lib.load.return_value = expected_res
        # act
        result = self.json_config_parser.parse(config_file=self.config_file)
        # verify
        self.assertEqual(result, expected_res)
