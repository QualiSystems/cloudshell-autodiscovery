import unittest

import mock

from autodiscovery.commands import RunFromReportCommand
from autodiscovery.exceptions import ReportableException


class TestRunFromReportCommand(unittest.TestCase):
    def setUp(self):
        self.data_processor = mock.MagicMock()
        self.report = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.cs_session_manager = mock.MagicMock()
        self.output = mock.MagicMock()
        self.run_command = RunFromReportCommand(data_processor=self.data_processor,
                                                report=self.report,
                                                logger=self.logger,
                                                cs_session_manager=self.cs_session_manager,
                                                output=self.output,
                                                autoload=True)

    def test_execute(self):
        """Check that method will upload discovered device"""
        entry = mock.MagicMock()
        handler = mock.MagicMock()
        self.run_command.vendor_type_handlers_map = mock.MagicMock(__getitem__=mock.MagicMock(return_value=handler))
        self.report.entries = [entry]
        # act
        self.run_command.execute(additional_vendors_data=None)
        # verify
        self.cs_session_manager.get_session.assert_called_once_with(cs_domain=entry.domain)

        handler.upload.assert_called_once_with(entry=entry,
                                               vendor=self.data_processor.load_vendor_config().get_vendor(),
                                               cs_session=self.cs_session_manager.get_session())
        self.report.generate.assert_called_once_with()

    def test_execute_handles_exception(self):
        """Check that method will handle Exception and will generate report"""
        handler = mock.MagicMock()
        self.run_command.vendor_type_handlers_map = mock.MagicMock(__getitem__=mock.MagicMock(return_value=handler))
        handler.upload = mock.MagicMock(side_effect=Exception())
        # act
        self.run_command.execute(additional_vendors_data=None)
        # verify
        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()
