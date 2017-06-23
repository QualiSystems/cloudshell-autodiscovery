import unittest

import mock
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.handlers import NetworkingTypeHandler


class TestNetworkingTypeHandler(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.networking_handler = NetworkingTypeHandler(logger=self.logger, autoload=True)

    def test_discover(self):
        """Check that method will return Entry with updated attributes"""
        entry = mock.MagicMock()
        vendor_settings = mock.MagicMock()
        cli_creds = mock.MagicMock()
        model_type = mock.MagicMock()
        device_os = mock.MagicMock(get_device_model_type=mock.MagicMock(return_value=model_type))
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))

        self.networking_handler._get_cli_credentials = mock.MagicMock(return_value=cli_creds)

        # act
        result = self.networking_handler.discover(entry=entry,
                                                  vendor=vendor,
                                                  vendor_settings=vendor_settings)

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(entry.model_type, model_type)

    def test_discover_no_cli_creds(self):
        """Check that method will add comment to the Entry if there is no valid CLI credentials"""
        entry = mock.MagicMock(user=None, password=None, enable_password=None)
        vendor = mock.MagicMock()
        vendor_settings = mock.MagicMock()
        self.networking_handler._get_cli_credentials = mock.MagicMock(return_value=None)

        # act
        result = self.networking_handler.discover(entry=entry,
                                                  vendor=vendor,
                                                  vendor_settings=vendor_settings)

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(entry.comment, "Unable to discover device user/password/enable password")
        self.assertIsNone(entry.user)
        self.assertIsNone(entry.password)
        self.assertIsNone(entry.enable_password)

    def test_upload_2_generation_shell(self):
        """Check that method will create CloudShell resource 2-nd generation and autoload it"""
        entry = mock.MagicMock()
        device_os = mock.MagicMock()
        families = {"second_gen": mock.MagicMock()}
        device_os.families.get.return_value = families
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))
        second_gen = families["second_gen"]
        cs_session = mock.MagicMock()
        resource_name = "test resource name"
        self.networking_handler._upload_resource = mock.MagicMock(return_value=resource_name)
        attributes = {
            ResourceModelsAttributes.ENABLE_SNMP: "False",
            ResourceModelsAttributes.SNMP_READ_COMMUNITY: entry.snmp_community,
            ResourceModelsAttributes.USER: entry.user,
            ResourceModelsAttributes.PASSWORD: entry.password,
            ResourceModelsAttributes.ENABLE_PASSWORD: entry.enable_password
        }

        # act
        self.networking_handler.upload(entry=entry,
                                       vendor=vendor,
                                       cs_session=cs_session)
        # verify
        self.networking_handler._upload_resource.assert_called_once_with(cs_session=cs_session,
                                                                         entry=entry,
                                                                         resource_family=second_gen["family_name"],
                                                                         resource_model=second_gen["model_name"],
                                                                         driver_name=second_gen["driver_name"],
                                                                         attribute_prefix="{}.".format(
                                                                             second_gen["model_name"]))

    def test_upload_1_generation_shell(self):
        """Check that method will create CloudShell resource 1-nd generation and autoload it"""
        entry = mock.MagicMock()
        device_os = mock.MagicMock()
        families = {"first_gen": mock.MagicMock()}
        device_os.families.get.return_value = families
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))
        first_gen = families["first_gen"]
        cs_session = mock.MagicMock()
        resource_name = "test resource name"
        self.networking_handler._upload_resource = mock.MagicMock(return_value=resource_name)

        # act
        self.networking_handler.upload(entry=entry,
                                       vendor=vendor,
                                       cs_session=cs_session)
        # verify
        self.networking_handler._upload_resource.assert_called_once_with(cs_session=cs_session,
                                                                         entry=entry,
                                                                         resource_family=first_gen["family_name"],
                                                                         resource_model=first_gen["model_name"],
                                                                         driver_name=first_gen["driver_name"])

    def test_upload_2_generation_shell_failed(self):
        """Check that method will upload 1-nd generation shell if 2-nd generation one failed"""
        entry = mock.MagicMock()
        device_os = mock.MagicMock()
        families = {"first_gen": mock.MagicMock(),
                    "second_gen": mock.MagicMock()}

        device_os.families.get.return_value = families
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))
        first_gen = families["first_gen"]
        second_gen = families["second_gen"]
        cs_session = mock.MagicMock()
        resource_name = "test resource name"
        self.networking_handler._upload_resource = mock.MagicMock(
            side_effect=[
                None,
                resource_name])

        attributes = {
            ResourceModelsAttributes.ENABLE_SNMP: "False",
            ResourceModelsAttributes.SNMP_READ_COMMUNITY: entry.snmp_community,
            ResourceModelsAttributes.USER: entry.user,
            ResourceModelsAttributes.PASSWORD: entry.password,
            ResourceModelsAttributes.ENABLE_PASSWORD: entry.enable_password
        }

        # act
        self.networking_handler.upload(entry=entry,
                                       vendor=vendor,
                                       cs_session=cs_session)
        # verify
        self.networking_handler._upload_resource.assert_any_call(cs_session=cs_session,
                                                                 entry=entry,
                                                                 resource_family=second_gen["family_name"],
                                                                 resource_model=second_gen["model_name"],
                                                                 driver_name=second_gen["driver_name"],
                                                                 attribute_prefix="{}.".format(
                                                                     second_gen["model_name"]))

        self.networking_handler._upload_resource.assert_any_call(cs_session=cs_session,
                                                                 entry=entry,
                                                                 resource_family=first_gen["family_name"],
                                                                 resource_model=first_gen["model_name"],
                                                                 driver_name=first_gen["driver_name"])
