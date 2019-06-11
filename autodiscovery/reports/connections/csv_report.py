from autodiscovery.reports.connections.base import AbstractConnectionsReport
from autodiscovery.reports.excel import AbstractExcelReport


class CSVReport(AbstractExcelReport, AbstractConnectionsReport):
    pass
