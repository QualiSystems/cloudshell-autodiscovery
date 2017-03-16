from console import ConsoleReport
from excel import ExcelReport


REPORTS_MAP = {
    "console": ConsoleReport,
    "excel": ExcelReport
}
DEFAULT_REPORT_TYPE = "excel"
REPORT_TYPES = REPORTS_MAP.keys()


def get_report(report_file, report_type):
    """Get Report object for the given type

    :param str report_file:
    :param str report_type:
    :rtype: AbstractReport
    """
    report_class = REPORTS_MAP.get(report_type)
    return report_class(report_file)
