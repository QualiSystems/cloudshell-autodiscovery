import unittest

import mock

from autodiscovery.data_processors import JsonDataProcessor


class TestJsonDataProcessor(unittest.TestCase):
    def setUp(self):
        self.filename = "example.json"
        self.logger = mock.MagicMock()
        self.json_data_processor = JsonDataProcessor(logger=self.logger)

    @mock.patch("autodiscovery.data_processors.config")
    @mock.patch("autodiscovery.data_processors.utils")
    def test_prepare_file_path(self, utils, config):
        full_path = mock.MagicMock()
        utils.get_full_path.return_value = full_path
        # act
        result = self.json_data_processor._prepare_file_path(filename=self.filename)
        # verify
        self.assertEqual(result, full_path)
        utils.get_full_path.assert_called_once_with(config.DATA_FOLDER, self.filename)

    @mock.patch("autodiscovery.data_processors.json")
    @mock.patch("autodiscovery.data_processors.open")
    def test_save(self, open, json):
        data = mock.MagicMock()
        file_path = mock.MagicMock()
        self.json_data_processor._prepare_file_path = mock.MagicMock(return_value=file_path)
        # act
        self.json_data_processor._save(data=data, filename=self.filename)
        # verify
        self.json_data_processor._prepare_file_path.assert_called_once_with(self.filename)
        open.assert_called_once_with(file_path, "w")
        json.dump.assert_called_once_with(data,
                                          open().__enter__(),
                                          indent=4,
                                          sort_keys=True)

    @mock.patch("autodiscovery.data_processors.json")
    @mock.patch("autodiscovery.data_processors.open")
    def test_load(self, open, json):
        file_path = mock.MagicMock()
        data = mock.MagicMock()
        json.load.return_value = data
        self.json_data_processor._prepare_file_path = mock.MagicMock(return_value=file_path)
        # act
        result = self.json_data_processor._load(filename=self.filename)
        # verify
        self.assertEqual(result, data)
        self.json_data_processor._prepare_file_path.assert_called_once_with(self.filename)
        open.assert_called_once_with(file_path, "r")
        json.load.assert_called_once_with(open().__enter__())

    @mock.patch("autodiscovery.data_processors.config")
    def test_save_vendor_enterprise_numbers(self, config):
        data = mock.MagicMock()
        self.json_data_processor._save = mock.MagicMock()
        # act
        self.json_data_processor.save_vendor_enterprise_numbers(data=data)
        # verify
        self.json_data_processor._save.assert_called_once_with(data=data,
                                                               filename=config.VENDOR_ENTERPRISE_NUMBERS_FILE)

    @mock.patch("autodiscovery.data_processors.config")
    def test_load_vendor_enterprise_numbers(self, config):
        """Check that method will properly merge initial vendors config with the additional one"""
        data = mock.MagicMock()
        self.json_data_processor._load = mock.MagicMock(return_value=data)
        # act
        result = self.json_data_processor.load_vendor_enterprise_numbers()
        # verify
        self.assertEqual(result, data)
        self.json_data_processor._load.assert_called_once_with(filename=config.VENDOR_ENTERPRISE_NUMBERS_FILE)

    def test_merge_vendors_data(self):
        """Check that method will properly merge initial vendors config with the additional one"""
        conf_data = [
            {
                "name": "Cisco",
                "default_os": "IOS",
                "operation_systems": [
                    {
                        "name": "IOS",
                        "default_model": "switch",
                    },
                    {
                        "name": "IOSXR",
                        "default_model": "router",
                    }
                ]
            },
            {
                "name": "Raritan",
                "default_prompt": "#",
                "family_name": "PDU",
                "model_name": "Raritan PDU",
                "driver_name": "Raritan PDU Driver"
            }
        ]
        additional_data = [
            {
                "name": "Cisco",
                "default_os": "IOS-EXTENDED",
                "operation_systems": [
                    {
                        "name": "IOS-EXTENDED",
                        "default_model": "switch",
                    },
                    {
                        "name": "IOSXR",
                        "default_model": "switch",
                    }
                ]
            },
            {
                "name": "Huawei",
                "default_os": "VPR",
                "operation_systems": [
                    {
                        "name": "VRP",
                        "default_model": "switch",
                    }
                ]
            },
        ]
        expected_data = [
            {
                "name": "Cisco",
                "default_os": "IOS-EXTENDED",
                "operation_systems": [
                    {
                        "name": "IOS-EXTENDED",
                        "default_model": "switch",
                    },
                    {
                        "name": "IOSXR",
                        "default_model": "switch",
                    },
                    {
                        "name": "IOS",
                        "default_model": "switch",
                    }
                ]
            },
            {
                "name": "Huawei",
                "default_os": "VPR",
                "operation_systems": [
                    {
                        "name": "VRP",
                        "default_model": "switch",
                    }
                ]
            },
            {
                "name": "Raritan",
                "default_prompt": "#",
                "family_name": "PDU",
                "model_name": "Raritan PDU",
                "driver_name": "Raritan PDU Driver"
            },
        ]
        # act
        result = self.json_data_processor._merge_vendors_data(conf_data, additional_data)
        # verify
        self.assertEqual(result, expected_data)

    @mock.patch("autodiscovery.data_processors.config")
    @mock.patch("autodiscovery.data_processors.models")
    def test_load_vendor_config(self, models, config):
        """Check that method will return VendorDefinitionCollection model"""
        vendors_collection = mock.MagicMock()
        models.VendorDefinitionCollection.return_value = vendors_collection
        additional_vendors_data = mock.MagicMock()
        vendors_data = mock.MagicMock()
        self.json_data_processor._merge_vendors_data = mock.MagicMock()
        self.json_data_processor._load = mock.MagicMock(return_value=vendors_data)
        # act
        result = self.json_data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)
        # verify
        self.assertEqual(result, vendors_collection)
        self.json_data_processor._load.assert_called_once_with(filename=config.VENDORS_CONFIG_FILE)
        self.json_data_processor._merge_vendors_data.assert_called_once_with(conf_data=vendors_data,
                                                                             additional_data=additional_vendors_data)
