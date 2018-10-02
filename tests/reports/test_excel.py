import collections
import unittest

import mock

from autodiscovery.reports.excel import AbstractExcelReport


class TestExcelReport(unittest.TestCase):
    def setUp(self):
        with mock.patch("autodiscovery.reports.base.AbstractEntry") as entry_class:
            class TestedClass(AbstractExcelReport):
                @property
                def _header_entry_map(self):
                    return collections.OrderedDict([("SNMP READ COMMUNITY", "snmp_read_community")])

                @property
                def entry_class(self):
                    return entry_class

        self.entry_class = entry_class
        self.file_name = "test_file_name.xlsx"
        self.excel_report = TestedClass(file_name=self.file_name)

    @mock.patch("autodiscovery.reports.excel.xlsxwriter")
    def test_generate(self, xlsxwriter):
        """Check that method will create Workbook and close it in the end"""
        workbook = mock.MagicMock()
        worksheet = mock.MagicMock()
        workbook.add_worksheet.return_value = worksheet
        xlsxwriter.Workbook.return_value = workbook
        # act
        self.excel_report.generate()
        # verify
        xlsxwriter.Workbook.assert_called_once_with(self.file_name)
        workbook.add_worksheet.assert_called_once_with()
        workbook.close.assert_called_once_with()

    @mock.patch("autodiscovery.reports.excel.load_workbook")
    def test_parse_entries_from_file(self, load_workbook):
        wb = mock.MagicMock()
        wb_sheet = wb.active
        wb_sheet.max_row = 2
        load_workbook.return_value = wb
        entry = mock.MagicMock()
        self.entry_class.return_value = entry
        # act
        result = self.excel_report.parse_entries_from_file(report_file=self.file_name)
        # verify
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], entry)
        load_workbook.assert_called_once_with(self.file_name)
