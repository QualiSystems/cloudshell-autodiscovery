import unittest

import mock

from autodiscovery.models import VendorDefinitionCollection
from autodiscovery.models import VendorCLICredentials
from autodiscovery.models import VendorSettingsCollection
from autodiscovery.models import CLICredentials
from autodiscovery.models import NetworkingVendorDefinition
from autodiscovery.models import BaseVendorDefinition
from autodiscovery.models import OperationSystem


class TestVendorDefinitionCollection(unittest.TestCase):
    def setUp(self):
        self.expected_vendor = mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=True))
        self.vendors = [mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False)),
                        mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False)),
                        self.expected_vendor,
                        mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False))]
        self.vendors_collection = VendorDefinitionCollection(vendors=self.vendors)

    def test_get_vendor(self):
        """Check that method will return correct vendor from the vemdors list"""
        vendor_name = "test_vendor_name"
        # act
        result = self.vendors_collection.get_vendor(vendor_name=vendor_name)
        # verify
        self.assertEqual(result, self.expected_vendor)


class TestBaseVendorDefinition(unittest.TestCase):
    def setUp(self):
        self.name = "test_vendor_name"
        self.aliases = ["Test", "[Tt]est2", "test3"]
        self.vendor_definition = BaseVendorDefinition(name=self.name,
                                                      aliases=self.aliases,
                                                      vendor_type=mock.MagicMock(),
                                                      default_prompt=mock.MagicMock(),
                                                      enable_prompt=mock.MagicMock())

    def test_check_vendor_name_names_are_equal(self):
        """Check that method will check if the names are equals before checking in aliases"""
        self.vendor_definition.check_in_aliases = mock.MagicMock()
        # act
        result = self.vendor_definition.check_vendor_name(vendor_name=self.name)
        # verify
        self.assertTrue(result)
        self.vendor_definition.check_in_aliases.assert_not_called()

    def test_check_vendor_name_name_is_in_aliases(self):
        """Check that method will check name in the aliases and return True"""
        vendor_name = "test2"
        self.vendor_definition.check_in_aliases = mock.MagicMock(return_value=True)
        # act
        result = self.vendor_definition.check_vendor_name(vendor_name=vendor_name)
        # verify
        self.assertTrue(result)
        self.vendor_definition.check_in_aliases.assert_called_once_with(vendor_name)

    def test_check_vendor_name_name_is_not_in_aliases(self):
        """Check that method will return False if names aren't equal and name is not in the aliases"""
        vendor_name = "some vendor"
        self.vendor_definition.check_in_aliases = mock.MagicMock(return_value=False)
        # act
        result = self.vendor_definition.check_vendor_name(vendor_name=vendor_name)
        # verify
        self.assertFalse(result)
        self.vendor_definition.check_in_aliases.assert_called_once_with(vendor_name)

    def test_check_in_aliases(self):
        """Check that method will return True if vendor name is in aliases"""
        vendor_name = "test2"
        # act
        result = self.vendor_definition.check_in_aliases(vendor_name=vendor_name)
        # verify
        self.assertTrue(result)

    def test_check_in_aliases_no(self):
        """Check that method will return False if vendor name is not in aliases"""
        vendor_name = "test10"
        # act
        result = self.vendor_definition.check_in_aliases(vendor_name=vendor_name)
        # verify
        self.assertFalse(result)


class TestNetworkingVendorDefinition(unittest.TestCase):
    def setUp(self):
        self.name = "test_vendor_name"
        self.aliases = ["Test", "[Tt]est2", "test3"]
        self.default_os = "default_os"
        self.operation_systems = [mock.MagicMock(aliases=[]), mock.MagicMock(aliases=[])]
        self.vendor_definition = NetworkingVendorDefinition(name=self.name,
                                                            aliases=self.aliases,
                                                            vendor_type=mock.MagicMock(),
                                                            default_prompt=mock.MagicMock(),
                                                            enable_prompt=mock.MagicMock(),
                                                            default_os=self.default_os,
                                                            operation_systems=self.operation_systems)

    def test_get_device_os_find_os_by_aliases(self):
        """Check that method will return OS from the list if system description matches one of the aliases"""
        expected_os = mock.MagicMock(aliases=["Test OS"])
        system_description = "description for Test OS."
        self.vendor_definition.operation_systems = [mock.MagicMock(aliases=["test alias"]),
                                                    mock.MagicMock(aliases=[]),
                                                    expected_os]
        # act
        result = self.vendor_definition.get_device_os(system_description=system_description)
        # verify
        self.assertEqual(result, expected_os)

    def test_get_device_os_calls_get_default_device_os(self):
        """Check that method will call get_default_device_os method to get default OS if any alias matches"""
        expected_os = mock.MagicMock()
        self.vendor_definition.get_default_device_os = mock.MagicMock(return_value=expected_os)
        system_description = "description for Test OS."
        # act
        result = self.vendor_definition.get_device_os(system_description=system_description)
        # verify
        self.assertEqual(result, expected_os)

    def test_get_default_device_os_no_default_value(self):
        """Check that method will return None if there is no default device OS"""
        self.vendor_definition.default_os = None
        # act
        result = self.vendor_definition.get_default_device_os()
        # verify
        self.assertIsNone(result)

    def test_get_default_device(self):
        """Check that method will return OS from the list by its default name"""
        expected_os = mock.MagicMock()
        expected_os.name = self.vendor_definition.default_os
        self.vendor_definition.operation_systems = [mock.MagicMock(),
                                                    expected_os,
                                                    mock.MagicMock()]
        # act
        result = self.vendor_definition.get_default_device_os()
        # verify
        self.assertEqual(result, expected_os)


class TestOperationSystem(unittest.TestCase):
    def setUp(self):
        self.name = "test OS"
        self.operation_sys = OperationSystem(name=self.name,
                                             aliases=mock.MagicMock(),
                                             default_model=mock.MagicMock(),
                                             models_map=mock.MagicMock(),
                                             families=mock.MagicMock())

    def test_get_device_model_type(self):
        """Check that method will return correct device model type by its aliases"""
        system_description = "Test OS"
        expected_model = "expected model"
        self.operation_sys.models_map = [
            {"aliases": ["some alias", "some alias2"], "model": "test model 1"},
            {"aliases": ["some alias", "[Tt]est OS", "some alias2"], "model": expected_model},
            {"aliases": ["some alias", "some alias2"], "model": "test model 3"}]
        # act
        result = self.operation_sys.get_device_model_type(system_description=system_description)
        # verify
        self.assertEqual(result, expected_model)

    def test_get_device_model_type_return_default_model_type(self):
        """Check that method will return default model type if any alias matches"""
        system_description = "Test OS"
        self.operation_sys.models_map = [
            {"aliases": ["some alias", "some alias2"], "model": "test model 1"}]
        # act
        result = self.operation_sys.get_device_model_type(system_description=system_description)
        # verify
        self.assertEqual(result, self.operation_sys.default_model)

    def test_get_resource_family(self):
        """Check that method will retrieve correct resource family name from the families map"""
        model_type = "router"
        expected_family = "router family"
        self.operation_sys.families = {
            model_type: {
                "family_name": expected_family
            }
        }
        # act
        result = self.operation_sys.get_resource_family(model_type=model_type)
        # verify
        self.assertEqual(result, expected_family)

    def test_get_resource_model(self):
        """Check that method will retrieve correct resource model name from the models map"""
        model_type = "router"
        expected_model = "router model"
        self.operation_sys.families = {
            model_type: {
                "model_name": expected_model
            }
        }
        # act
        result = self.operation_sys.get_resource_model(model_type=model_type)
        # verify
        self.assertEqual(result, expected_model)


class TestCLICredentials(unittest.TestCase):
    def test_equality(self):
        """Check that instances with the same attributes will be equals"""
        self.assertEquals(CLICredentials(user="test user", password="test password", enable_password="test password"),
                          CLICredentials(user="test user", password="test password", enable_password="test password"))


class TestVendorCLICredentials(unittest.TestCase):
    def setUp(self):
        self.name = "test OS"
        self.vendor_creds = VendorCLICredentials(name="vendor name",
                                                 cli_credentials=[mock.MagicMock()])

    def test_update_valid_creds(self):
        """Check that method will add valid_creds to the cli_credentials list at the first place"""
        valid_creds = mock.MagicMock()
        # act
        self.vendor_creds.update_valid_creds(valid_creds=valid_creds)
        # verify
        self.assertIn(valid_creds, self.vendor_creds.cli_credentials)
        self.assertEqual(valid_creds, self.vendor_creds.cli_credentials[0])


class TestVendorSettingsCollection(unittest.TestCase):
    def setUp(self):
        self.vendor_name = "test vendor"
        self.cli_creds = VendorSettingsCollection(vendor_settings={
            "default": {
                "cli-credentials": [
                    {
                        "user": "test user 1",
                        "password": "test password 1",
                    }
                ],
                "folder-path": "test folder path"
            },
            self.vendor_name: {
                "cli-credentials": [
                    {
                        "user": "test vendor user 1",
                        "password": "test vendor password 1",
                    }
                ]
            }
        })

    def test_get_creds_by_vendor(self):
        """Check that method will return credentials with the same vendor name"""
        vendor = mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=True))
        # act
        result = self.cli_creds.get_creds_by_vendor(vendor=vendor)
        # verify
        self.assertEqual(result.name, self.vendor_name)

    def test_get_creds_by_vendor_default_creds(self):
        """Check that method will return default credentials"""
        vendor = mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False))
        # act
        result = self.cli_creds.get_creds_by_vendor(vendor=vendor)
        # verify
        self.assertEqual(result.name, "default")
