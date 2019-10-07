import unittest

import mock

from autodiscovery.handlers import NetworkingTypeHandler


class TestNetworkingTypeHandler(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.networking_handler = NetworkingTypeHandler(
            logger=self.logger, autoload=True
        )

    def test_discover(self):
        """Check that method will return Entry with updated attributes."""
        entry = mock.MagicMock()
        vendor_settings = mock.MagicMock()
        cli_creds = mock.MagicMock()
        model_type = mock.MagicMock()
        device_os = mock.MagicMock(
            get_device_model_type=mock.MagicMock(return_value=model_type)
        )
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))

        self.networking_handler._get_cli_credentials = mock.MagicMock(
            return_value=cli_creds
        )

        # act
        result = self.networking_handler.discover(
            entry=entry, vendor=vendor, vendor_settings=vendor_settings
        )

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(entry.model_type, model_type)

    def test_discover_no_cli_creds(self):
        """Check that method will add correct comment to the Entry."""
        entry = mock.MagicMock(user=None, password=None, enable_password=None)
        vendor = mock.MagicMock()
        vendor_settings = mock.MagicMock()
        self.networking_handler._get_cli_credentials = mock.MagicMock(return_value=None)

        # act
        result = self.networking_handler.discover(
            entry=entry, vendor=vendor, vendor_settings=vendor_settings
        )

        # verify
        self.assertEqual(result, entry)
        self.assertEqual(
            entry.comment, "Unable to discover device user/password/enable password"
        )
        self.assertIsNone(entry.user)
        self.assertIsNone(entry.password)
        self.assertIsNone(entry.enable_password)

    def test_upload_2_generation_shell(self):
        """Check that method will create CloudShell resource 2-nd generation."""
        entry = mock.MagicMock()
        device_os = mock.MagicMock()
        family = mock.MagicMock()
        device_os.families.get.return_value = family
        vendor = mock.MagicMock(get_device_os=mock.MagicMock(return_value=device_os))
        cs_session = mock.MagicMock()
        resource_name = "test resource name"
        self.networking_handler._upload_resource = mock.MagicMock(
            return_value=resource_name
        )

        # act
        self.networking_handler.upload(
            entry=entry, vendor=vendor, cs_session=cs_session
        )
        # verify
        self.networking_handler._upload_resource.assert_called_once_with(
            cs_session=cs_session,
            entry=entry,
            resource_family=family["family_name"],
            resource_model=family["model_name"],
            driver_name=family["driver_name"],
            attribute_prefix="{}.".format(family["model_name"]),
        )
