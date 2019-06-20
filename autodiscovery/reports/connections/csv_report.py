from autodiscovery.reports.connections.base import AbstractConnectionsReport
from autodiscovery.reports.csv_report import AbstractCSVReport


class CSVReport(AbstractCSVReport, AbstractConnectionsReport):
    pass
