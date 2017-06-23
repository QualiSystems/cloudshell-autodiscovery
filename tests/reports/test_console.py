import unittest

import mock

from autodiscovery.reports import ExcelReport


class TestExcelReport(unittest.TestCase):
    def setUp(self):
        self.file_name = "test_report.xlsx"
        self.excel_report = ExcelReport(file_name=self.file_name)

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
        worksheet.set_column.assert_called()
        workbook.close.assert_called_once_with()

    @mock.patch("autodiscovery.reports.excel.Entry")
    @mock.patch("autodiscovery.reports.excel.load_workbook")
    def test_parse_entries_from_file(self, load_workbook, entry_class):
        wb = mock.MagicMock()
        wb_sheet = wb.active
        wb_sheet.max_row = 2
        load_workbook.return_value = wb
        entry = mock.MagicMock()
        entry_class.return_value = entry
        # act
        result = self.excel_report.parse_entries_from_file(report_file=self.file_name)
        # verify
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], entry)
        load_workbook.assert_called_once_with(self.file_name)
