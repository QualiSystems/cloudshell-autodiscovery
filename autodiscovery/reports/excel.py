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
            self.SOURCE_PORT_HEADER: 30,
            self.TARGET_PORT_HEADER: 30,
            self.DOMAIN_HEADER: 20,
            self.STATUS_HEADER: 25,
            self.COMMENT_HEADER: 40,
        }


# worksheet.set_column(prepare_column(self.IP_COLUMN, self.VENDOR_COLUMN), 20)
# worksheet.set_column(prepare_column(self.SYS_OBJ_COLUMN), 30)
# worksheet.set_column(prepare_column(self.DESCRIPTION_COLUMN), 50)
# worksheet.set_column(prepare_column(self.SNMP_COMMUNITY_COLUMN), 30)
# worksheet.set_column(prepare_column(self.MODEL_TYPE_COLUMN, self.DEVICE_NAME_COLUMN), 20)
# worksheet.set_column(prepare_column(self.DOMAIN_COLUMN), 20)
# worksheet.set_column(prepare_column(self.FOLDER_COLUMN), 20)
# worksheet.set_column(prepare_column(self.ATTRIBUTES_COLUMN), 25)
# worksheet.set_column(prepare_column(self.STATUS_COLUMN), 25)
# worksheet.set_column(prepare_column(self.COMMENT_COLUMN), 40)