from collections import OrderedDict

from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.reports.base import AbstractParsableReport
from autodiscovery.reports.discovery.excel import ExcelReport
from autodiscovery.reports.discovery.console import ConsoleReport
from autodiscovery.reports.discovery.csv_report import CSVReport


REPORTS = (CSVReport, ExcelReport, ConsoleReport)
REPORTS_MAP = OrderedDict([(report_cls.FILE_EXTENSION, report_cls) for report_cls in REPORTS])
DEFAULT_REPORT_TYPE = CSVReport.FILE_EXTENSION
REPORT_TYPES = REPORTS_MAP.keys()


def get_report(report_file, report_type=DEFAULT_REPORT_TYPE):
    """Get Report object for the given type

    :param str report_file:
    :param str report_type:
    :rtype: autodiscovery.reports.discovery.base.AbstractReport
    """
    report_cls = REPORTS_MAP.get(report_type)
    return report_cls(report_file)


def parse_report(report_file):
    """Parse report file and it's data to the Report object based on it's file extension

    :param report_file:
    :rtype: autodiscovery.reports.discovery.base.AbstractParsableReport
    """
    available_reports = [report_cls for report_cls in REPORTS if issubclass(report_cls, AbstractParsableReport)]

    for report_cls in available_reports:
        if report_file.endswith(".{}".format(report_cls.FILE_EXTENSION)):
            report = report_cls(report_file)
            report.parse_entries_from_file(report_file)
            return report

    raise AutoDiscoveryException("Invalid Report file format. Available formats are: {}".format(
        ", ".join([report.FILE_EXTENSION for report in available_reports])))
