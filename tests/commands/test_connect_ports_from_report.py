import unittest

import mock

from autodiscovery.commands import ConnectPortsFromReportCommand
from autodiscovery.exceptions import ReportableException


class TestConnectPortsFromReportCommand(unittest.TestCase):
    def setUp(self):
        self.report = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.cs_session_manager = mock.MagicMock()
        self.output = mock.MagicMock()
        self.connect_ports_command = ConnectPortsFromReportCommand(
            cs_session_manager=self.cs_session_manager,
            report=self.report,
            logger=self.logger,
            output=self.output,
        )

    def test_execute(self):
        """Check that method will call UpdatePhysicalConnection API command."""
        entry_data = mock.MagicMock()
        cs_session = mock.MagicMock()
        self.cs_session_manager.get_session.return_value = cs_session
        self.report.entries = [entry_data]
        # act
        self.connect_ports_command.execute()
        # verify
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=entry_data.domain
        )

        cs_session.UpdatePhysicalConnection.assert_called_once_with(
            resourceAFullPath=entry_data.source_port,
            resourceBFullPath=entry_data.target_port,
        )

        self.report.generate.assert_called_once_with()

    def test_execute_handles_reportable_exception(self):
        """Method should handle ReportableException and generate report."""
        entry = mock.MagicMock()
        self.cs_session_manager.get_session.side_effect = ReportableException()
        self.report.entries = [entry]
        # act
        self.connect_ports_command.execute()
        # verify
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=entry.domain
        )
        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()

    def test_execute_handles_exception(self):
        """Method should handle Exception and generate report."""
        entry = mock.MagicMock()
        self.cs_session_manager.get_session.side_effect = Exception()
        self.report.entries = [entry]
        # act
        self.connect_ports_command.execute()
        # verify
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=entry.domain
        )
        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()
