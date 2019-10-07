from collections import OrderedDict

from autodiscovery.reports import get_report as base_get_report
from autodiscovery.reports import parse_report as base_parse_report
from autodiscovery.reports.connections.console import ConsoleReport
from autodiscovery.reports.connections.csv_report import CSVReport
from autodiscovery.reports.connections.excel import ExcelReport

REPORTS = (CSVReport, ExcelReport, ConsoleReport)
REPORTS_MAP = OrderedDict(
    [(report_cls.FILE_EXTENSION, report_cls) for report_cls in REPORTS]
)
DEFAULT_REPORT_TYPE = CSVReport.FILE_EXTENSION
REPORT_TYPES = REPORTS_MAP.keys()


def get_report(report_file, report_type=DEFAULT_REPORT_TYPE):
    """Get Report object for the given type.

    :param str report_file:
    :param str report_type:
    :rtype: autodiscovery.reports.base.AbstractReport
    """
    return base_get_report(
        report_file=report_file, report_type=report_type, reports_map=REPORTS_MAP
    )


def parse_report(report_file):
    """Parse report file and it's data to the Report object based on it's file extension.

    :param report_file:
    :rtype: autodiscovery.reports.base.AbstractParsableReport
    """
    return base_parse_report(report_file=report_file, reports=REPORTS)
