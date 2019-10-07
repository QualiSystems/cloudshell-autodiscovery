from autodiscovery.reports.console import AbstractConsoleReport
from autodiscovery.reports.discovery.base import AbstractDiscoveryReport


class ConsoleReport(AbstractConsoleReport, AbstractDiscoveryReport):
    DESCRIPTION_COLUMN_WIDTH = 60
    COMMENT_COLUMN_WIDTH = 40

    @property
    def _header_column_width_map(self):
        """

        :return:
        """
        return {self.COMMENT_HEADER: 40, self.DESCRIPTION_HEADER: 60}
