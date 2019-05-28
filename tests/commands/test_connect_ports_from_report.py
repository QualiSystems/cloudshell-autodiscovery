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
        self.connect_ports_command = ConnectPortsFromReportCommand(cs_session_manager=self.cs_session_manager,
                                                                   report=self.report,
                                                                   logger=self.logger,
                                                                   output=self.output)

    def test_execute(self):
        """Check that method will call UpdatePhysicalConnection API command"""
        entry_data = mock.MagicMock()
        cs_session = mock.MagicMock()
        self.cs_session_manager.get_session.return_value = cs_session
        # act
        self.connect_ports_command.execute(parsed_entries=[entry_data])
        # verify
        self.report.edit_entry.assert_called_once_with(entry=entry_data)
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=self.report.edit_entry().__enter__().domain)

        cs_session.UpdatePhysicalConnection.assert_called_once_with(
            resourceAFullPath=entry_data.source_port,
            resourceBFullPath=entry_data.target_port)

        self.report.generate.assert_called_once_with()

    def test_execute_handles_reportable_exception(self):
        """Check that method will handle ReportableException and will generate report"""
        entry_data = mock.MagicMock()
        self.cs_session_manager.get_session.side_effect = ReportableException()
        # act
        self.connect_ports_command.execute(parsed_entries=[entry_data])

        # verify
        self.report.edit_entry.assert_called_once_with(entry=entry_data)
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=self.report.edit_entry().__enter__().domain)

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()

    def test_execute_handles_exception(self):
        """Check that method will handle Exception and will generate report"""
        entry_data = mock.MagicMock()
        self.cs_session_manager.get_session.side_effect = Exception()
        # act
        self.connect_ports_command.execute(parsed_entries=[entry_data])

        # verify
        self.report.edit_entry.assert_called_once_with(entry=entry_data)
        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=self.report.edit_entry().__enter__().domain)

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()
