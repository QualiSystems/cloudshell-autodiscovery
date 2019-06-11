from collections import OrderedDict

from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.reports.base import AbstractParsableReport
from autodiscovery.reports.connections.excel import ExcelReport
from autodiscovery.reports.connections.console import ConsoleReport
from autodiscovery.reports.connections.csv_report import CSVReport


REPORTS = (CSVReport, ExcelReport, ConsoleReport)
REPORTS_MAP = OrderedDict([(report_cls.FILE_EXTENSION, report_cls) for report_cls in REPORTS])
DEFAULT_REPORT_TYPE = CSVReport.FILE_EXTENSION
REPORT_TYPES = REPORTS_MAP.keys()


def get_report(report_file, report_type=DEFAULT_REPORT_TYPE):
    """Get Report object for the given type

    :param str report_file:
    :param str report_type:
    :rtype: autodiscovery.reports.connections.base.AbstractReport
    """
    report_class = REPORTS_MAP.get(report_type)
    return report_class(report_file)


def parse_report(report_file):
    """Parse report file and it's data to the Report object based on it's file extension

    :param report_file:
    :rtype: autodiscovery.reports.connections.base.AbstractParsableReport
    """
    available_reports = [report_cls for report_cls in REPORTS if issubclass(report_cls, AbstractParsableReport)]

    for report_cls in available_reports:
        if report_file.endswith("{}".format(report_cls.FILE_EXTENSION)):
            return report_cls(report_file)

    raise AutoDiscoveryException("Invalid Report file format. Available formats are: {}".format(
        ", ".join([report.FILE_EXTENSION for report in available_reports])))
