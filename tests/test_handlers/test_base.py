import unittest

import mock
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler


class TestAbstractHandler(unittest.TestCase):
    def setUp(self):
        class TestedClass(AbstractHandler):
            pass

        self.logger = mock.MagicMock()
        self.cs_session = mock.MagicMock()
        self.tested_instance = TestedClass(logger=self.logger, autoload=True)

    def test_discover_method_raises_exception_if_it_was_not_implemented(self):
        """Check that method will raise exception if it wasn't implemented in the child class"""
        with self.assertRaises(NotImplementedError):
            self.tested_instance.discover(entry=mock.MagicMock(),
                                          vendor=mock.MagicMock(),
                                          vendor_settings=mock.MagicMock())

    def test_upload_method_raises_exception_if_it_was_not_implemented(self):
        """Check that method will raise exception if it wasn't implemented in the child class"""
        with self.assertRaises(NotImplementedError):
            self.tested_instance.upload(entry=mock.MagicMock(),
                                        vendor=mock.MagicMock(),
                                        cs_session=mock.MagicMock())

    def test_add_resource_driver(self):
        """Check that method will call UpdateResourceDriver method on the CloudShell session instance"""
        resource_name = "test resource name"
        driver_name = "test driver name"
        # act
        self.tested_instance._add_resource_driver(cs_session=self.cs_session,
                                                  resource_name=resource_name,
                                                  driver_name=driver_name)
        # verify
        self.cs_session.UpdateResourceDriver.assert_called_once_with(resourceFullPath=resource_name,
                                                                     driverName=driver_name)

    def test_add_resource_driver_raises_reportable_exception(self):
        """Check that method will raise ReportableException if there is no given driver on the CloudShell"""
        resource_name = "test resource name"
        driver_name = "test driver name"
        self.cs_session.UpdateResourceDriver.side_effect = CloudShellAPIError(
            code=CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_DRIVER,
            message="",
            rawxml="")

        with self.assertRaisesRegexp(ReportableException, "is not installed"):
            self.tested_instance._add_resource_driver(cs_session=self.cs_session,
                                                      resource_name=resource_name,
                                                      driver_name=driver_name)

    @mock.patch("autodiscovery.handlers.base.AttributeNameValue")
    @mock.patch("autodiscovery.handlers.base.ResourceAttributesUpdateRequest")
    def test_create_cs_resource(self, resource_attributes_update_request_class, attribute_name_value_class):
        """Check that method will call create resource on the CloudShell and return resource name"""
        resource_name = "test resource name"
        resource_family = "test resource family"
        resource_model = "test resource model"
        driver_name = "test driver name"
        device_ip = "test device IP"
        folder_path = "test folder path"
        resource_attributes = mock.MagicMock()
        attr_name_value = mock.MagicMock()
        resource_attributes_update_request_class.return_value = resource_attributes
        attribute_name_value_class.return_value = attr_name_value

        # act
        result = self.tested_instance._create_cs_resource(cs_session=self.cs_session,
                                                          resource_name=resource_name,
                                                          resource_family=resource_family,
                                                          resource_model=resource_model,
                                                          device_ip=device_ip,
                                                          folder_path=folder_path)
        # verify
        self.assertEqual(result, resource_name)
        self.cs_session.CreateResource.assert_called_once_with(resourceFamily=resource_family,
                                                               resourceModel=resource_model,
                                                               resourceName=resource_name,
                                                               resourceAddress=device_ip,
                                                               folderFullPath=folder_path)

    def test_create_cs_resource_resource_name_is_taken(self):
        """Check that method will try to create resource one more time if given resource name is already taken"""
        resource_name = "test resource name"
        resource_family = "test resource family"
        resource_model = "test resource model"
        device_ip = "test device IP"
        folder_path = "test folder path"
        expected_resource_name = "{}-1".format(resource_name)
        self.tested_instance._add_resource_driver = mock.MagicMock()
        self.cs_session.CreateResource.side_effect = [
            CloudShellAPIError(code=CloudshellAPIErrorCodes.RESOURCE_ALREADY_EXISTS,
                               message="",
                               rawxml=""),
            None]

        result = self.tested_instance._create_cs_resource(cs_session=self.cs_session,
                                                          resource_name=resource_name,
                                                          resource_family=resource_family,
                                                          resource_model=resource_model,
                                                          device_ip=device_ip,
                                                          folder_path=folder_path)
        # verify
        self.assertEqual(result, expected_resource_name)

        self.cs_session.CreateResource.assert_any_call(resourceFamily=resource_family,
                                                       resourceModel=resource_model,
                                                       resourceName=resource_name,
                                                       resourceAddress=device_ip,
                                                       folderFullPath=folder_path)

        self.cs_session.CreateResource.assert_any_call(resourceFamily=resource_family,
                                                       resourceModel=resource_model,
                                                       resourceName=expected_resource_name,
                                                       resourceAddress=device_ip,
                                                       folderFullPath=folder_path)

    @mock.patch("autodiscovery.handlers.base.SSHDiscoverySession")
    @mock.patch("autodiscovery.handlers.base.TelnetDiscoverySession")
    def test_get_cli_credentials(self, telnet_session_class, ssh_session_class):
        """Check that method will create valid credentials for first working session"""
        vendor = mock.MagicMock()
        vendor_cli_creds = mock.MagicMock()
        vendor_settings = mock.MagicMock(get_creds_by_vendor=mock.MagicMock(return_value=vendor_cli_creds))
        device_ip = "device_ip"
        ssh_session = mock.MagicMock()
        telnet_session = mock.MagicMock()
        valid_creds = mock.MagicMock()
        telnet_session_class.return_value = telnet_session
        ssh_session_class.return_value = ssh_session
        ssh_session.check_credentials.return_value = valid_creds
        # act
        self.tested_instance._get_cli_credentials(vendor=vendor,
                                                  vendor_settings=vendor_settings,
                                                  device_ip=device_ip)
        # verify
        telnet_session_class.assert_called_once_with(device_ip)
        ssh_session_class.assert_called_once_with(device_ip)

        ssh_session.check_credentials.assert_called_once_with(cli_credentials=vendor_cli_creds,
                                                              default_prompt=vendor.default_prompt,
                                                              enable_prompt=vendor.enable_prompt,
                                                              logger=self.logger)

        vendor_cli_creds.update_valid_creds.assert_called_once_with(valid_creds)
        telnet_session.check_credentials.assert_not_called()

    @mock.patch("autodiscovery.handlers.base.SSHDiscoverySession")
    @mock.patch("autodiscovery.handlers.base.TelnetDiscoverySession")
    def test_get_cli_credentials_handles_exception(self, telnet_session_class, ssh_session_class):
        """Check that method will try another session if first one will raise Exception"""
        vendor = mock.MagicMock()
        vendor_cli_creds = mock.MagicMock()
        vendor_settings = mock.MagicMock(get_creds_by_vendor=mock.MagicMock(return_value=vendor_cli_creds))
        device_ip = "device_ip"
        ssh_session = mock.MagicMock()
        telnet_session = mock.MagicMock()
        valid_creds = mock.MagicMock()
        telnet_session_class.return_value = telnet_session
        ssh_session_class.return_value = ssh_session
        ssh_session.check_credentials.side_effect = Exception()
        telnet_session.check_credentials.return_value = valid_creds
        # act
        self.tested_instance._get_cli_credentials(vendor=vendor,
                                                  vendor_settings=vendor_settings,
                                                  device_ip=device_ip)
        # verify
        ssh_session.check_credentials.assert_called_once_with(cli_credentials=vendor_cli_creds,
                                                              default_prompt=vendor.default_prompt,
                                                              enable_prompt=vendor.enable_prompt,
                                                              logger=self.logger)

        telnet_session.check_credentials.assert_called_once_with(cli_credentials=vendor_cli_creds,
                                                                 default_prompt=vendor.default_prompt,
                                                                 enable_prompt=vendor.enable_prompt,
                                                                 logger=self.logger)

        vendor_cli_creds.update_valid_creds.assert_called_once_with(valid_creds)
