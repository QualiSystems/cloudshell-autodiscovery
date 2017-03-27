import unittest

from autodiscovery.reports import ConsoleReport
from autodiscovery.reports import ExcelReport
from autodiscovery.reports import get_report


class TestInitReports(unittest.TestCase):

    def test_get_report_for_excel_format(self):
        """Check that method will return ExcelReport instance for the excel report type"""
        report_file = "report.xlsx"
        report_type = "excel"
        # act
        report = get_report(report_file, report_type)
        # verify
        self.assertIsInstance(report, ExcelReport)

    def test_get_report_for_console_format(self):
        """Check that method will return ConsoleReport instance for the console report type"""
        report_file = "report"
        report_type = "console"
        # act
        report = get_report(report_file, report_type)
        # verify
        self.assertIsInstance(report, ConsoleReport)
