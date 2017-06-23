import unittest

import mock

from autodiscovery.cli_sessions.base import AbstractDiscoverySession
from autodiscovery.exceptions import AutoDiscoveryException


class TestAbstractDiscoverySession(unittest.TestCase):
    def setUp(self):
        class TestedClass(AbstractDiscoverySession):
            def _receive(self):
                pass

            def _send(self):
                pass

            def connect(self):
                pass

            def disconnect(self):
                pass

        self.device_ip = "test_device_ip"
        self.logger = mock.MagicMock()
        self.tested_class = TestedClass
        self.tested_instance = TestedClass(self.device_ip)

    def test_check_credentials_raises_exception_if_it_was_not_implemented(self):
        """Check that method will raise exception if it wasn't implemented in the child class"""
        cli_credentials = mock.MagicMock()
        default_prompt = mock.MagicMock()
        enable_prompt = mock.MagicMock()

        with self.assertRaises(NotImplementedError):
            self.tested_instance.check_credentials(cli_credentials=cli_credentials,
                                                   default_prompt=default_prompt,
                                                   enable_prompt=enable_prompt,
                                                   logger=self.logger)

    @mock.patch("autodiscovery.cli_sessions.base.collections")
    @mock.patch("autodiscovery.cli_sessions.base.re")
    def test_check_enable_password(self, re, collections):
        """Check that method will return checked valid creds instance"""
        cli_credentials = mock.MagicMock()
        valid_creds = mock.MagicMock()
        enable_prompt = "#"
        output_str = "#"
        self.tested_instance.prepare_credentials_action_map = mock.MagicMock()
        self.tested_instance.hardware_expect = mock.MagicMock()
        re.search.return_value = False
        # act
        result = self.tested_instance._check_enable_password(enable_prompt=enable_prompt,
                                                             cli_credentials=cli_credentials,
                                                             valid_creds=valid_creds,
                                                             output_str=output_str,
                                                             logger=self.logger)
        # verify
        self.assertEqual(result, valid_creds)
        self.tested_instance.prepare_credentials_action_map.assert_called_once_with(
            cli_credentials=cli_credentials,
            creds_key="enable_password",
            valid_creds=valid_creds)

        self.tested_instance.hardware_expect.assert_called_once_with(
            self.tested_instance.ENABLE_MODE_COMMAND,
            expected_string=enable_prompt,
            timeout=self.tested_instance._timeout,
            logger=self.logger,
            action_map=collections.OrderedDict(),
            check_action_loop_detector=False)

        self.assertIsNotNone(valid_creds.enable_password)

    @mock.patch("autodiscovery.cli_sessions.base.re")
    def test_check_enable_password_set_enable_password_attr_to_none(self, re):
        """Check that method will set enable_password attr to None if any Exception occurs in the hardware_expect"""
        cli_credentials = mock.MagicMock()
        valid_creds = mock.MagicMock()
        enable_prompt = "#"
        output_str = "#"
        self.tested_instance.prepare_credentials_action_map = mock.MagicMock()
        self.tested_instance.hardware_expect = mock.MagicMock(side_effect=Exception)
        re.search.return_value = False
        # act
        result = self.tested_instance._check_enable_password(enable_prompt=enable_prompt,
                                                             cli_credentials=cli_credentials,
                                                             valid_creds=valid_creds,
                                                             output_str=output_str,
                                                             logger=self.logger)
        # verify
        self.assertEqual(result, valid_creds)
        self.assertIsNone(valid_creds.enable_password)

    def test_prepare_credentials_action_map_returns_callable_object(self):
        """Check that method will return callable object"""
        cli_credentials = mock.MagicMock()
        valid_creds = mock.MagicMock()
        creds_key = "creds_key"
        # act
        result = self.tested_class.prepare_credentials_action_map(cli_credentials=cli_credentials,
                                                                  valid_creds=valid_creds,
                                                                  creds_key=creds_key)
        # verify
        self.assertTrue(callable(result))

    def test_prepare_credentials_action_map_1111(self):
        """Check that method will update valid_creds object with possible credentials"""
        valid_creds = mock.MagicMock()
        creds_value = "creds_value"
        cli_credentials = mock.MagicMock(cli_credentials=[mock.MagicMock(creds_key=creds_value)])
        session = mock.MagicMock()
        # act
        wrapped = self.tested_class.prepare_credentials_action_map(cli_credentials=cli_credentials,
                                                                   valid_creds=valid_creds,
                                                                   creds_key="creds_key")
        # verify
        wrapped(session=session, logger=self.logger)
        session.send_line.assert_called_once_with(creds_value, self.logger)
        self.assertEqual(valid_creds.creds_key, creds_value)

    def test_prepare_credentials_action_map_raise_exception_if_all_creds_arent_valid(self):
        """Check that method will raise AutoDiscoveryException if any credentials aren't valid"""
        valid_creds = mock.MagicMock()
        creds_key = "creds_key"
        cli_credentials = mock.MagicMock(cli_credentials=[])
        session = mock.MagicMock()
        # act
        wrapped = self.tested_class.prepare_credentials_action_map(cli_credentials=cli_credentials,
                                                                   valid_creds=valid_creds,
                                                                   creds_key=creds_key)
        # verify
        with self.assertRaisesRegexp(AutoDiscoveryException, "All given credentials aren't valid"):
            wrapped(session=session, logger=self.logger)
