from autodiscovery.reports.connections.excel import ExcelReport
from autodiscovery.reports.connections.console import ConsoleReport


REPORTS_MAP = {
    "console": ConsoleReport,
    "excel": ExcelReport
}
DEFAULT_REPORT_TYPE = "excel"
REPORT_TYPES = REPORTS_MAP.keys()


def get_report(report_file, report_type=DEFAULT_REPORT_TYPE):
    """Get Report object for the given type

    :param str report_file:
    :param str report_type:
    :rtype: autodiscovery.reports.base.AbstractReport
    """
    report_class = REPORTS_MAP.get(report_type)
    return report_class(report_file)
