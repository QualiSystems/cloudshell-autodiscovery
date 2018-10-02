from autodiscovery.reports.connections.base import AbstractConnectionsReport
from autodiscovery.reports.excel import AbstractExcelReport


class ExcelReport(AbstractExcelReport, AbstractConnectionsReport):
    DEFAULT_REPORT_FILE = "connect_ports_report{}".format(AbstractExcelReport.FILE_EXTENSION)

    @property
    def _header_column_width_map(self):
        """

        :return:
        """
        return {
            self.SOURCE_PORT_HEADER: 30,
            self.TARGET_PORT_HEADER: 30,
            self.DOMAIN_HEADER: 20,
            self.STATUS_HEADER: 25,
            self.COMMENT_HEADER: 40,
        }
