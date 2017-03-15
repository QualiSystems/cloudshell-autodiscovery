import re

import xlsxwriter

from autodiscovery.reports.base import AbstractReport


class ExcelReport(AbstractReport):
    DEFAULT_REPORT_FILE = "report.xlsx"
    COMMENT_COLUMN = "J:J"  # todo: for all columns

    def __init__(self, file_name=None):
        """

        :param str file_name:
        """
        super(ExcelReport, self).__init__()
        if file_name is None:
            file_name = self.DEFAULT_REPORT_FILE

        self.file_name = file_name

    def generate(self):
        """Save report for all discovered devices into the excel file"""
        workbook = xlsxwriter.Workbook(self.file_name)
        worksheet = workbook.add_worksheet()
        table_data = [self.HEADER]

        for entry in self._entries:
            description = re.sub("\s+", " ", entry.description)
            table_data.append((entry.ip, entry.vendor, entry.sys_object_id, description, entry.snmp_community,
                               entry.user, entry.password, entry.enable_password, entry.model_type, entry.device_name,
                               entry.status, entry.comment))

        for row_num, row in enumerate(table_data):
            for col_num, col in enumerate(row):
                worksheet.write(row_num, col_num, col)

        # set bold header
        worksheet.set_row(0, None, workbook.add_format({'bold': True}))
        # format columns width
        worksheet.set_column("A:B", 20)
        worksheet.set_column("C:C", 30)
        worksheet.set_column("D:D", 50)
        worksheet.set_column("E:E", 30)
        worksheet.set_column("F:H", 20)
        worksheet.set_column("I:I", 30)
        worksheet.set_column(self.COMMENT_COLUMN, 40)

        workbook.close()
