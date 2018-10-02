from autodiscovery.reports.discovery.base import AbstractDiscoveryReport
from autodiscovery.reports.excel import AbstractExcelReport


class ExcelReport(AbstractExcelReport, AbstractDiscoveryReport):
    DEFAULT_REPORT_FILE = "discovery_report{}".format(AbstractExcelReport.FILE_EXTENSION)

    @property
    def _header_column_width_map(self):
        """

        :return:
        """
        return {
            self.IP_HEADER: 20,
            self.VENDOR_HEADER: 20,
            self.SYS_OBJ_ID_HEADER: 30,
            self.DESCRIPTION_HEADER: 50,
            self.SNMP_READ_COMMUNITY_HEADER: 30,
            self.MODEL_TYPE_HEADER: 20,
            self.DEVICE_NAME_HEADER: 20,
            self.DOMAIN_HEADER: 20,
            self.FOLDER_HEADER: 20,
            self.ATTRIBUTES_HEADER: 25,
            self.ADDED_TO_CLOUDSHELL_HEADER: 25,
            self.COMMENT_HEADER: 40,
        }
