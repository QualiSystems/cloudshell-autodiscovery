import unittest

import mock
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.handlers import PDUTypeHandler


class TestPDUTypeHandler(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.pdu_handler = PDUTypeHandler(logger=self.logger)

    def test_discover(self):
        """Check that method will return Entry with updated attributes"""
        entry = mock.MagicMock()
        cli_credentials = mock.MagicMock()
        cli_creds = mock.MagicMock()
        vendor = mock.MagicMock()
        self.pdu_handler._get_cli_credentials = mock.MagicMock(return_value=cli_creds)

        # act
        result = self.pdu_handler.discover(entry=entry,
                                           vendor=vendor,
                                           cli_credentials=cli_credentials)

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(entry.user, cli_creds.user)
        self.assertEqual(entry.password, cli_creds.password)

    def test_discover_no_cli_creds(self):
        """Check that method will add comment to the Entry if there is no valid CLI credentials"""
        entry = mock.MagicMock(user=None, password=None)
        vendor = mock.MagicMock()
        cli_credentials = mock.MagicMock()
        self.pdu_handler._get_cli_credentials = mock.MagicMock(return_value=None)

        # act
        result = self.pdu_handler.discover(entry=entry,
                                           vendor=vendor,
                                           cli_credentials=cli_credentials)

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(entry.comment, "Unable to discover device user/password")
        self.assertIsNone(entry.user)
        self.assertIsNone(entry.password)

    def test_upload(self):
        """Check that method will create CloudShell resource and autoload it"""
        entry = mock.MagicMock()
        vendor = mock.MagicMock()
        cs_session = mock.MagicMock()
        resource_name = "test resource name"
        self.pdu_handler._create_cs_resource = mock.MagicMock(return_value=resource_name)
        attributes = {
            ResourceModelsAttributes.USER: entry.user,
            ResourceModelsAttributes.PASSWORD: entry.password,
        }

        # act
        self.pdu_handler.upload(entry=entry,
                                vendor=vendor,
                                cs_session=cs_session)
        # verify
        self.pdu_handler._create_cs_resource.assert_called_once_with(cs_session=cs_session,
                                                                     resource_name=entry.device_name,
                                                                     resource_family=vendor.family_name,
                                                                     resource_model=vendor.model_name,
                                                                     driver_name=vendor.driver_name,
                                                                     device_ip=entry.ip,
                                                                     attributes=attributes)

        cs_session.AutoLoad.assert_called_once_with(resource_name)
