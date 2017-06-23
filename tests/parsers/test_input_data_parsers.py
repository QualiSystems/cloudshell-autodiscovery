import unittest

import mock

from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.parsers.input_data_parsers import AbstractInputDataParser
from autodiscovery.parsers.input_data_parsers import JSONInputDataParser
from autodiscovery.parsers.input_data_parsers import YAMLInputDataParser
from autodiscovery.parsers.input_data_parsers import get_input_data_parser


class TestInputDataParsers(unittest.TestCase):
    def test_get_input_data_parser_for_json_format(self):
        """Check that method will return JSONInputDataParser instance"""
        # act
        result = get_input_data_parser(file_name="test_file.json")
        # verify
        self.assertIsInstance(result, JSONInputDataParser)

    def test_get_input_data_parser_for_yaml_format(self):
        """Check that method will return YAMLInputDataParser instance"""
        # act
        result = get_input_data_parser(file_name="test_file.yml")
        # verify
        self.assertIsInstance(result, YAMLInputDataParser)

    def test_get_input_data_parser_invalid_file_format(self):
        """Check that method will raise AutoDiscoveryException if provided file is in invalid format"""
        with self.assertRaisesRegexp(AutoDiscoveryException, "Invalid Input Data file format"):
            get_input_data_parser(file_name="test_file.invalid")


class TestAbstractInputDataParser(unittest.TestCase):
    def setUp(self):
        class TestedClass(AbstractInputDataParser):
            pass

        self.tested_instance = TestedClass()
        self.input_file = mock.MagicMock()

    def test_find_ips(self):
        """Check that method will return range of IPs between start IP and last IP"""
        expected_res = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]
        # act
        result = self.tested_instance._find_ips(start_ip=u"10.0.0.1", last_ip=u"10.0.0.4")
        # verify
        self.assertEqual(result, expected_res)

    @mock.patch("autodiscovery.parsers.input_data_parsers.models.DeviceIPRange")
    def test_parse_devices_ips(self, device_ip_range_class):
        """Check that method will return list of DeviceIPRange models"""
        first_parsed_ips = mock.MagicMock()
        second_parsed_ips = mock.MagicMock()
        self.tested_instance._find_ips = mock.MagicMock(side_effect=[first_parsed_ips, second_parsed_ips])
        device_ip_range = mock.MagicMock()
        device_ip_range_class.return_value = device_ip_range
        expected_res = [device_ip_range, device_ip_range, device_ip_range]

        devices_ips = [
            {
                "range": "192.168.10.3-45",
                "domain": "Test Domain"
            },
            {
                "range": "192.168.8.1-9.10"
            },
            "192.168.42.235"]

        # act
        result = self.tested_instance._parse_devices_ips(devices_ips)
        # verify
        self.assertEqual(result, expected_res)
        device_ip_range_class.assert_any_call(ip_range=first_parsed_ips, domain="Test Domain")
        device_ip_range_class.assert_any_call(ip_range=second_parsed_ips, domain=None)
        device_ip_range_class.assert_any_call(ip_range=["192.168.42.235"], domain=None)

        self.tested_instance._find_ips.assert_any_call(start_ip=u"192.168.10.3",
                                                       last_ip=u"192.168.10.45")
        self.tested_instance._find_ips.assert_any_call(start_ip=u"192.168.8.1",
                                                       last_ip=u"192.168.9.10")

    def test_parse_method_raises_exception_if_it_was_not_implemented(self):
        """Check that method will raise exception if it wasn't implemented in the child class"""
        with self.assertRaises(NotImplementedError):
            self.tested_instance.parse(input_file=self.input_file)


class TestYAMLInputDataParser(unittest.TestCase):
    def setUp(self):
        self.input_parser = YAMLInputDataParser()
        self.input_file = "test_input.yml"

    @mock.patch("autodiscovery.parsers.input_data_parsers.open")
    @mock.patch("autodiscovery.parsers.input_data_parsers.yaml")
    @mock.patch("autodiscovery.parsers.input_data_parsers.models.InputDataModel")
    def test_parse(self, input_data_model_class, yaml, open):
        """Check that method returns InputDataModel instance"""
        expected_res = mock.MagicMock()
        input_data_model_class.return_value = expected_res
        self.input_parser._parse_devices_ips = mock.MagicMock()
        # act
        result = self.input_parser.parse(input_file=self.input_file)
        # verify
        self.assertEqual(result, expected_res)
        self.input_parser._parse_devices_ips.assert_called_once()
        yaml.load.assert_called_once()


class TestJSONInputDataParser(unittest.TestCase):
        def setUp(self):
            self.input_parser = JSONInputDataParser()
            self.input_file = "test_input.json"

        @mock.patch("autodiscovery.parsers.input_data_parsers.open")
        @mock.patch("autodiscovery.parsers.input_data_parsers.json")
        @mock.patch("autodiscovery.parsers.input_data_parsers.models.InputDataModel")
        def test_parse(self, input_data_model_class, json, open):
            """Check that method returns InputDataModel instance"""
            expected_res = mock.MagicMock()
            input_data_model_class.return_value = expected_res
            self.input_parser._parse_devices_ips = mock.MagicMock()
            # act
            result = self.input_parser.parse(input_file=self.input_file)
            # verify
            self.assertEqual(result, expected_res)
            self.input_parser._parse_devices_ips.assert_called_once()
            json.load.assert_called_once()
