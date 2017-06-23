import unittest

import mock

from autodiscovery.cli_sessions import TelnetDiscoverySession
from autodiscovery.exceptions import AutoDiscoveryException


class TestTelnetDiscoverySession(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.device_ip = "test_device_ip"
        self.telnet_session = TelnetDiscoverySession(self.device_ip)

    @mock.patch("autodiscovery.cli_sessions.telnet.CLICredentials")
    @mock.patch("autodiscovery.cli_sessions.telnet.OrderedDict")
    def test_check_credentials(self, ordered_dict_class, cli_credentials_class):
        credentials = mock.MagicMock()
        cli_credentials = mock.MagicMock(cli_credentials=[credentials])
        default_prompt = "#"
        enable_prompt = "$"
        valid_creds = mock.MagicMock()
        output_str = mock.MagicMock()
        self.telnet_session._check_enable_password = mock.MagicMock(return_value=valid_creds)
        self.telnet_session._handler = mock.MagicMock()
        self.telnet_session.hardware_expect = mock.MagicMock(return_value=output_str)
        cli_credentials_class.return_value = valid_creds
        # act
        result = self.telnet_session.check_credentials(cli_credentials=cli_credentials,
                                                       default_prompt=default_prompt,
                                                       enable_prompt=enable_prompt,
                                                       logger=self.logger)
        # verify
        self.assertEqual(result, valid_creds)
        self.telnet_session._handler.close.assert_called_once_with()
        self.telnet_session.hardware_expect.assert_called_once_with(None,
                                                                    expected_string="#|$",
                                                                    timeout=self.telnet_session._timeout,
                                                                    logger=self.logger,
                                                                    action_map=ordered_dict_class(),
                                                                    check_action_loop_detector=False)

        self.telnet_session._check_enable_password.assert_called_once_with(enable_prompt=enable_prompt,
                                                                           cli_credentials=cli_credentials,
                                                                           valid_creds=valid_creds,
                                                                           output_str=output_str,
                                                                           logger=self.logger)
