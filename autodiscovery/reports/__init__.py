from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.reports.base import AbstractParsableReport


def get_report(report_file, report_type, reports_map):
    """Get Report object for the given type

    :param str report_file:
    :param str report_type:
    :param disct reports_map:
    :rtype: autodiscovery.reports.base.AbstractReport
    """
    report_class = reports_map.get(report_type)
    return report_class(report_file)


def parse_report(report_file, reports):
    """Parse report file and it's data to the Report object based on it's file extension

    :param str report_file:
    :param tuple reports:
    :rtype: autodiscovery.reports.base.AbstractParsableReport
    """
    available_reports = [report_cls for report_cls in reports if issubclass(report_cls, AbstractParsableReport)]

    for report_cls in available_reports:
        if report_file.endswith(".{}".format(report_cls.FILE_EXTENSION)):
            report = report_cls(report_file)
            report.parse_entries_from_file(report_file)
            return report

    raise AutoDiscoveryException("Invalid Report file format. Available formats are: {}".format(
        ", ".join([report.FILE_EXTENSION for report in available_reports])))
