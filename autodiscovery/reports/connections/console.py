from autodiscovery.reports.connections.base import AbstractConnectionsReport
from autodiscovery.reports.console import AbstractConsoleReport


class ConsoleReport(AbstractConsoleReport, AbstractConnectionsReport):
    DEFAULT_REPORT_FILE = "connections-report.txt"

    @property
    def _header_column_width_map(self):
        """

        :return:
        """
        return {
            self.COMMENT_HEADER: 40,
        }
