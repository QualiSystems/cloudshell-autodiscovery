from textwrap import wrap

from terminaltables import AsciiTable

from autodiscovery.reports.discovery.base import AbstractReport


class ConsoleReport(AbstractReport):
    DESCRIPTION_COLUMN_WIDTH = 60
    COMMENT_COLUMN_WIDTH = 40
    DEFAULT_REPORT_FILE = "discovery-report.txt"

    def __init__(self, file_name=None):
        """

        :param str file_name:
        """
        super(ConsoleReport, self).__init__()
        if file_name is None:
            file_name = self.DEFAULT_REPORT_FILE

        self.file_name = file_name

    def generate(self):
        """Print report for all discovered devices to the console"""
        empty_row = ("",) * len(self.HEADER)
        table_data = [self.HEADER]

        for entry in self._entries:
            description = '\n'.join(wrap(str(entry.description), self.DESCRIPTION_COLUMN_WIDTH))
            comment = '\n'.join(wrap(str(entry.comment), self.COMMENT_COLUMN_WIDTH))
            table_data.extend([(entry.ip, entry.vendor, entry.sys_object_id, description, entry.snmp_community,
                                entry.model_type, entry.device_name, entry.domain, entry.folder_path,
                                entry.formatted_attrs, entry.status, comment),
                               empty_row])  # add an empty row between records

        table = AsciiTable(table_data)

        with open(self.file_name, "w") as report_file:
            report_file.write(table.table)
