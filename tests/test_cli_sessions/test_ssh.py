import unittest

import mock

from autodiscovery.cli_sessions import SSHDiscoverySession
from autodiscovery.exceptions import AutoDiscoveryException


class TestSSHDiscoverySession(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.device_ip = "test_device_ip"
        self.ssh_session = SSHDiscoverySession(self.device_ip)

    def test_check_credentials(self):
        """Check that method will return valid creds instance"""
        credentials = mock.MagicMock()
        cli_credentials = mock.MagicMock(cli_credentials=[credentials])
        default_prompt = "#"
        enable_prompt = "$"
        valid_creds = mock.MagicMock()
        output_str = mock.MagicMock()
        self.ssh_session._check_enable_password = mock.MagicMock(return_value=valid_creds)
        self.ssh_session._handler = mock.MagicMock()
        self.ssh_session.hardware_expect = mock.MagicMock(return_value=output_str)
        # act
        result = self.ssh_session.check_credentials(cli_credentials=cli_credentials,
                                                    default_prompt=default_prompt,
                                                    enable_prompt=enable_prompt,
                                                    logger=self.logger)
        # verify
        self.assertEqual(result, valid_creds)
        self.ssh_session._handler.close.assert_called_once_with()
        self.ssh_session.hardware_expect.assert_called_once_with(None,
                                                                 expected_string="#|$",
                                                                 timeout=self.ssh_session._timeout,
                                                                 logger=self.logger)

        self.ssh_session._check_enable_password.assert_called_once_with(enable_prompt=enable_prompt,
                                                                        cli_credentials=cli_credentials,
                                                                        valid_creds=credentials,
                                                                        output_str=output_str,
                                                                        logger=self.logger)

    def test_check_credentials_no_valid_credentials(self):
        """Check that method will raise AutoDiscoveryException if any credentials aren't valid"""
        cli_credentials = mock.MagicMock(cli_credentials=[])
        default_prompt = "#"
        enable_prompt = "$"

        # verify
        with self.assertRaisesRegexp(AutoDiscoveryException, "All given credentials aren't valid"):
            self.ssh_session.check_credentials(cli_credentials=cli_credentials,
                                               default_prompt=default_prompt,
                                               enable_prompt=enable_prompt,
                                               logger=self.logger)
