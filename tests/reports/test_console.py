import collections
import unittest

import mock

from autodiscovery.reports.console import AbstractConsoleReport


class TestConsoleReport(unittest.TestCase):
    def setUp(self):
        class TestedClass(AbstractConsoleReport):
            @property
            def _header_entry_map(self):
                return collections.OrderedDict([("SNMP READ COMMUNITY", "snmp_read_community")])

        self.file_name = "test_filename"
        self.console_report = TestedClass(file_name=self.file_name)

    @mock.patch("autodiscovery.reports.console.AsciiTable")
    @mock.patch("autodiscovery.reports.console.open")
    def test_generate(self, open, ascii_table_class):
        """Check that method will write table data to the report file"""
        report_file = mock.MagicMock()
        table = mock.MagicMock()
        ascii_table_class.return_value = table
        open.return_value = mock.MagicMock(__enter__=mock.MagicMock(return_value=report_file))
        # act
        self.console_report.generate()
        # verify
        report_file.write.assert_called_once_with(table.table)
